__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

from flask import request, flash, redirect, url_for, send_file, send_from_directory
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.plag_dao import PlagiarismDAO
from service.similarDocument_dao import SimilarDocumentDAO
from service.analysisHistory_dao import AnalysisHistoryDAO
from util.constants.error_codes import HttpErrorCode
from util.error_handlers.exceptions import ExceptionBuilder, BadRequest
from controller import elasticsearch
import json
from settings import app, config
import os
from werkzeug.utils import secure_filename
import PyPDF2
from flask import jsonify
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import pdfplumber



UPLOAD_FOLDER = os.path.abspath(os.getcwd()) + '/documents'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Método que utiliza pdfplumber
def convert_pdf_to_txt(path):
    all_text = '' # new line
    with pdfplumber.open(path) as pdf:
        for pdf_page in pdf.pages:
            single_page_text = pdf_page.extract_text()
            # separate each page's text with newline
            all_text = all_text + '\n' + single_page_text
    return all_text

#Método que utiliza PDFMiner
def convert_pdf_to_txt_2(path):
    resource_manager = PDFResourceManager()
    fake_file_handle = StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

class Document(BaseController):
    plag_dao: PlagiarismDAO = inject(PlagiarismDAO)
    similarDocDao: SimilarDocumentDAO = inject(SimilarDocumentDAO)
    analysisHistoryDao: AnalysisHistoryDAO = inject(AnalysisHistoryDAO)
    elasticsearhobj = elasticsearch.ElasticSearchFunction()

    def __init__(self):
        self.events = []

    def saveDocument(self, data, option):
        content = data.get('content', '')
        title = data.get('title', '')
        fileName = data.get('fileName', '')
        description = data.get('description', '')
        responsibleCode = data.get('responsibleCode', '')
        announcementCode = data.get('announcementCode', '')
        indexDoc = data.get('indexDoc', '')
        documentType = data.get('documentType', '')
        if title:
            # Se agrega el documento en la BD
            if (option == "save"):
                if content:
                    # Se agrega el documento en la BD
                    doc = self.plag_dao.create_doc(content, title, fileName, description=description, responsibleCode=responsibleCode, announcementCode=announcementCode, documentType=documentType)
                    # Se agrega el documento al índice en elasticsearh
                    if indexDoc == 1:
                        self.elasticsearhobj.add(doc.to_dict_es())
                    message='Document added successfully!'
                else:
                    ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'content').throw()
            else:
                id = data.get('id', '')
                doc = self.plag_dao.edit_doc(id, title, description=description, responsibleCode=responsibleCode, announcementCode=announcementCode)
                #TODO - implementar la actualización en ELASTICSEARCH
                message='Document updated successfully!'

        else:
            ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'title').throw()

        return Response(status_code=201, message=message)

    @intercept()
    def post(self, *args, **kwargs):
        """Adds a new document to repo"""
        data = request.get_json(force=True)
        return self.saveDocument(data, "save")

    @intercept()
    def get(self):
        """
        Fetches all the documents(paginated).
        :return:
        """
        res = self.plag_dao.get_docs_info(page=int(request.args.get("page", 1)),
                                    per_page=int(request.args.get("per_page", 10)), all='all' in request.args)
        
        docs_info = dict(data=[d for d in res['data']], count=res['count'])
        return Response(data=docs_info)

    @intercept()
    def put(self, *args, **kwargs):
        """Adds a new document to repo"""
        data = request.get_json(force=True)
        return self.saveDocument(data, "update")

    
    @intercept()
    def delete(self, *args, **kwargs):
        try:
            id = request.get_json()
            #Marcar como eliminado el documento
            self.plag_dao.deleteDocument(id)
            #Marcar como eliminado el registro del documento similar
            self.similarDocDao.deleteDocument(id)
            #Marcar loas análsisi como eliminados
            self.analysisHistoryDao.deleteAnalysis(id)
            #Eliminar el documento del índice
            self.elasticsearhobj.delete_by_query(id)
        except:
            return Response(status_code=500, message='Error to delete Document!')
        return Response(status_code=201, message='Document deleted successfully!')
    
    @app.route("/api/v1/plagiarism/uploadFile", methods=['GET','POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                return jsonify(status_code=500, message='No file part!')
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                return jsonify(status_code=500, message='No selected file!')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(config['UPLOAD_FOLDER'], filename))
                #fhandle = open(os.path.join(config['UPLOAD_FOLDER'], filename), 'rb')
                content_pdf = convert_pdf_to_txt(os.path.join(config['UPLOAD_FOLDER'], filename))
                #TODO -- Obtener el responsibleCode y announcementCode
                data =  {
                    'content':content_pdf, 
                    'title':request.form.get("title"), 
                    'description':request.form.get("description"), 
                    'fileName':filename,
                    'indexDoc':request.form.get("indexDoc"),
                    'responsibleCode':request.form.get("responsibleCode"), 
                    'announcementCode':request.form.get("announcementCode"),
                    'documentType':request.form.get("documentType")
                }
                try:
                    doc = Document()
                    doc.saveDocument(data, "save")
                except:
                    #TODO - validar que el documento no exista previamente para eliminar / agregar
                    os.remove(os.path.join(config['UPLOAD_FOLDER'], filename))
                    return jsonify(status_code=500, message='Error to save document in BD or Elastic!')
                return jsonify(status_code=201, message='Document added successfully!')
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''

    @app.route('/api/v1/plagiarism/downloadFile/<path:filename>', methods=['GET', 'POST'])
    def download(filename):
        path = os.path.join(config['UPLOAD_FOLDER'], filename)
        return send_file(path, as_attachment=True)
        #return send_file(path_or_file=path, as_attachment=True)

    @app.route("/api/v1/plagiarism/indexDocument", methods=['POST'])
    def indexDocument():
        try:
            data = request.get_json()
            # Se obtiene la información del documento
            document = Document()
            doc = document.plag_dao.get_doc(data['id'])
            response_es = document.elasticsearhobj.add(doc)
            document.plag_dao.updateStatus(data['id'], 2) #Status a indexado
        except:
            return jsonify(status_code=500, message='Error to index document in Elastic!')
        return jsonify(status_code=200, message='Document idexed successfully!')

    @app.route("/api/v1/plagiarism/getDocumentInfo/<id>", methods=['GET'])
    def getDocumentInfo(id):
        # Se obtiene la información del documento
        document = Document()
        doc = document.plag_dao.get_doc_info(id)
        return jsonify(status_code=201, message='Report returned successfully!', data=doc)

