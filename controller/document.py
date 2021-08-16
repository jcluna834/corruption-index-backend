__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

from flask import request, flash, redirect, url_for
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.plag_dao import PlagiarismDAO
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
    elasticsearhobj = elasticsearch.ElasticSearchFunction()

    def __init__(self):
        self.events = []

    def saveDocument(self, data):
        content = data.get('content', '')
        title = data.get('title', '')
        description = data.get('description', '')
        responsibleCode = data.get('responsibleCode', '')
        announcementCode = data.get('announcementCode', '')
        indexDoc = data.get('indexDoc', '')
        if content and title:
            # Se agrega el documento en la BD
            doc = self.plag_dao.create_doc(content, title, description=description, responsibleCode=responsibleCode, announcementCode=announcementCode)
            # Se agrega el documento al índice en elasticsearh
            if indexDoc == 1:
                self.elasticsearhobj.add(doc.to_dict_es())
        else:
            ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'content', 'title').throw()

        return Response(status_code=201, message='Document added successfully!')

    @intercept()
    def post(self, *args, **kwargs):
        """Adds a new document to repo"""
        data = request.get_json(force=True)
        return self.saveDocument(data)

    @intercept()
    def get(self):
        """
        Fetches all the documents(paginated).
        :return:
        """
        res = self.plag_dao.get_docs(page=int(request.args.get("page", 1)),
                                     per_page=int(request.args.get("per_page", 10)), all='all' in request.args)
        docs_info = dict(data=[d.to_dict() for d in res['data']], count=res['count'])
        return Response(data=docs_info)
    
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
                data =  {'content':content_pdf, 'title':request.form.get("title"), 'description':request.form.get("description"), 'indexDoc':request.form.get("indexDoc"),
                    'responsibleCode':request.form.get("responsibleCode"), 'announcementCode':request.form.get("announcementCode")}
                try:
                    doc = Document()
                    doc.saveDocument(data)
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
