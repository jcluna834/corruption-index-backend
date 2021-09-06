__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

import json
import re
from flask import request
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.plag_detector import PlagiarismDetector
from service.plag_dao import PlagiarismDAO
from service.analysisHistory_dao import AnalysisHistoryDAO
from service.announcement_dao import AnnouncementDAO
from service.similarDocument_dao import SimilarDocumentDAO
from util.constants.error_codes import HttpErrorCode
from util.error_handlers.exceptions import ExceptionBuilder, BadRequest
from controller import elasticsearch
from controller import functions_plag
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from pymongo import MongoClient
from settings import app, config, JSONEncoder
from flask import jsonify
from bson.objectid import ObjectId
from datetime import datetime


client = MongoClient('localhost:27017')
__collection__ = 'PlagiarismDetection'

#Se descarga sinonimos al inicio
'''import nltk
nltk.download('punkt')
'''
stopwords = stopwords.words('spanish')

def getCurrentUser():
    return config['USERAUTHID']

def getCurrentAnnouncement():
    return config['ANNOUNCEMENTID']

class PlagiarismDetection(BaseController):
    plag_detector: PlagiarismDetector = inject(PlagiarismDetector)
    elasticsearhobj = elasticsearch.ElasticSearchFunction()
    functions_plag_obj = functions_plag.FunctionsPlagiarism()
    plag_dao: PlagiarismDAO = inject(PlagiarismDAO)
    analyisHistory_dao: AnalysisHistoryDAO = inject(AnalysisHistoryDAO)
    announcement_dao: AnnouncementDAO = inject(AnnouncementDAO)
    similarDocument_dao: SimilarDocumentDAO = inject(SimilarDocumentDAO)

    def similarityAnalisis(self, data, analysisType, similarDocumentID= '', documentId='', entityId=''):
        #response_skl = []
        response_es = []
        my_uncommon_response = []
        similarDocuments = []
        # Se divide en párrafos el texto recibido
        token_text = sent_tokenize(data)
        for paragraph_text in token_text:
            # Se detecta similitud haciendo uso de ElasticSearh
            if(analysisType == 0): #analysis global
                responseES = self.elasticsearhobj.searchByContent(paragraph_text)
            else: #analysis entre 2 documentos
                responseES = self.elasticsearhobj.searchBetweenDocs(paragraph_text, similarDocumentID)
            highlight_response = []

            # Se evalua cada párrafo retornado
            for highlight in responseES['hits']['hits'][0]['highlight']['content']:
                parag_text_clean = self.functions_plag_obj.getStringClean(paragraph_text)
                highlight_clean = self.functions_plag_obj.getStringClean(highlight)
                uncommon_words = list(self.functions_plag_obj.getUncommonWords(parag_text_clean,highlight_clean))
                common_words = list(self.functions_plag_obj.getCommonWords(parag_text_clean,highlight_clean))
                my_uncommon_words = self.functions_plag_obj.getHighlightPerformance(uncommon_words,parag_text_clean)

                res_highlight_data = {
                    'content': highlight,
                    'levenshtein_distance': self.functions_plag_obj.getLevenshteinDistance(parag_text_clean, highlight_clean),
                    'similatiry_difflib': self.functions_plag_obj.getRatioSequenceMatcher(parag_text_clean, highlight_clean),
                    #'uncommon_words': uncommon_words,
                    'common_words': common_words,
                    'my_uncommon_words': my_uncommon_words
                }
                highlight_response.append(res_highlight_data)

            # Se arma la respuesta a entregar en API
            res_es_data = {
                'paragraph_text': paragraph_text,
                'similarity_score': responseES['hits']['hits'][0]['_score'],
                'similarity_percentage': responseES['hits']['hits'][0]['_score'],
                'doc_': responseES['hits']['hits'][0]['_source'],
                'highlight': highlight_response,
                'status': 0
            }
            response_es.append(res_es_data)
            similarDocuments.append(responseES['hits']['hits'][0]['_source']['id']) if responseES['hits']['hits'][0]['_source']['id'] not in similarDocuments else similarDocuments

        #Se agregan los documentos similares
        print("--------------------------------------")
        plagiarismDetection = PlagiarismDetection()
        if(analysisType == 0 and documentId != ''): #analysis global
            for similarDocID in similarDocuments:
                print("docID: " + similarDocID)
                exists = plagiarismDetection.similarDocument_dao.existsSimilarDoc(documentId, similarDocID)
                if (not exists):
                    plagiarismDetection.similarDocument_dao.createSimilarDocuments(documentId, similarDocID)

        # Respuesta final entregada en el POST
        super_res_data = {
            'response_elastic': response_es,
            'responsibleCode': getCurrentUser(),
            'announcementCode': getCurrentAnnouncement(),
            'documentID': documentId,
            'entityID': entityId,
            'AnalysisDate': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }

        # Save in collection MongoDB
        db = client.get_database(__collection__)
        collection = db.PlagiarismDetection
        collection.insert_one(super_res_data)

        analysis_response = super_res_data.copy()
        
        return analysis_response

    @intercept()
    def post(self, *args, **kwargs):
        """Detects plagiarism"""
        data = request.get_json(force=True)
        input_doc = data.get('text', None)
        if input_doc is None:
            ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'text').throw()
        
        analysisType = 0
        analysis_response = self.similarityAnalisis(input_doc, analysisType)
        return Response(status_code=200, message='Return info match', data=JSONEncoder().encode(analysis_response))
        

    @app.route("/api/v1/plagiarism/getReportsSimilarity", methods=['GET'])
    def getReportsSimilarity():
        db = client.get_database(__collection__)
        collection = db.PlagiarismDetection
        responseCollection = collection.find({"responsibleCode": getCurrentUser()})
        list_cur = list(responseCollection)
        return jsonify(status_code=201, message='Reports returned successfully!', count=len(list_cur), data=list_cur)

    @app.route("/api/v1/plagiarism/getReportsSimilarityByDocumentId_Collection/<documentID>", methods=['GET'])
    def getReportsSimilarityByDocumentId_Collection(documentID):
        db = client.get_database(__collection__)
        collection = db.PlagiarismDetection
        responseCollection = collection.find({"responsibleCode": getCurrentUser(), "documentID": documentID})
        list_cur = list(responseCollection)
        return jsonify(status_code=201, message='Reports returned successfully!', count=len(list_cur), data=list_cur)

    @app.route("/api/v1/plagiarism/getReportsSimilarityByDocumentId/<documentID>", methods=['GET'])
    def getReportsSimilarityByDocumentId(documentID):
        plagiarismDetection = PlagiarismDetection()
        analysisHistory = plagiarismDetection.analyisHistory_dao.analysisHistoryByDocumentCode(documentID)
        return jsonify(status_code=201, message='Reports returned successfully!', data=analysisHistory)


    @app.route("/api/v1/plagiarism/getReport/<id>", methods=['GET'])
    def getReport(id):
        db = client.get_database(__collection__)
        collection = db.PlagiarismDetection
        responseCollection = collection.find({"_id":ObjectId(id)})
        list_cur = list(responseCollection)
        return jsonify(status_code=201, message='Report returned successfully!', data=list_cur)

    @app.route("/api/v1/plagiarism/executeSimilarityAnalisis", methods=['POST'])
    def executeSimilarityAnalisis():
        try:
            data = request.get_json()
            # Se obtiene la información del documento
            plagiarismDetection = PlagiarismDetection()
            doc = plagiarismDetection.plag_dao.get_doc(data['id'])
            #Se crea el registro histórico de análisis
            analysisType = 0 #Análisis global
            analysisHistory = plagiarismDetection.analyisHistory_dao.create_analysisHistory(data['id'], 0, analysisType)
            #Se obtiene el entity_code
            announcement = plagiarismDetection.announcement_dao.get_announcement(doc['announcementCode'])
            #Se ejecuta el proceso de análsis de similitud
            analysisType = 0
            response_analysis = plagiarismDetection.similarityAnalisis(doc['content'], analysisType, 
                documentId=data['id'], entityId=announcement['entity_code']) #fijar a doc['content']
            #Status del documento a analizado
            plagiarismDetection.plag_dao.updateStatus(data['id'], 1) 
            #Status del histórico 
            #TODO obtener el id de json
            plagiarismDetection.analyisHistory_dao.edit_analysisHistory(analysisHistory.id, 1, response_analysis["_id"])
        except:
            return jsonify(status_code=500, message='Error to index document in Elastic!')
        return jsonify(status_code=200, success=True, message='Return info match', data=response_analysis)

    @app.route("/api/v1/plagiarism/executeSimilarityAnalisisBetweenDocs", methods=['POST'])
    def executeSimilarityAnalisisBetweenDocs():
        try:
            data = request.get_json()
            # Se obtiene la información del documento
            plagiarismDetection = PlagiarismDetection()
            doc = plagiarismDetection.plag_dao.get_doc(data['analysisDocumentCode'])

            #Se crea el registro histórico de análisis
            analysisType = 4 #Análisis entre documentos
            analysisHistory = plagiarismDetection.analyisHistory_dao.create_analysisHistory(data['analysisDocumentCode'], 0, 
                analysisType, similarDocumentCode=data['similarDocumentCode'])

            #Status del similar documento a analizado
            plagiarismDetection.similarDocument_dao.updateStatus(data['id'], 1) 
            
            #Se obtiene el entity_code
            announcement = plagiarismDetection.announcement_dao.get_announcement(doc['announcementCode'])
            #Se ejecuta el proceso de análsis de similitud
            analysisType = 1
            response_analysis = plagiarismDetection.similarityAnalisis(doc['content'], analysisType, 
                similarDocumentID=data['similarDocumentCode'],  documentId=data['analysisDocumentCode'], 
                entityId=announcement['entity_code']) #fijar a doc['content']

            #Status del histórico 
            #TODO obtener el id de json
            plagiarismDetection.analyisHistory_dao.edit_analysisHistory(analysisHistory.id, 1, response_analysis["_id"])
        except:
            return jsonify(status_code=500, message='Error to index document in Elastic!')

        return jsonify(status_code=200, success=True, message='Return info match', data=response_analysis)

    @app.route("/api/v1/plagiarism/SimulateExecuteSimilarityAnalisis", methods=['POST'])
    def SimulateExecuteSimilarityAnalisis():
        try:
            print("inicio")
            plagiarismDetection = PlagiarismDetection()
            data = request.get_json()
            analysisType = 0 #Análisis global
            plagiarismDetection.analyisHistory_dao.create_analysisHistory(data['id'], 0, analysisType)
            announcement = plagiarismDetection.announcement_dao.get_announcement(data['announcementCode'])
            import time
            time.sleep(20)
            print("termino")
        except:
            return jsonify(status_code=500, message='Error to index document in Elastic!')
        return jsonify(status_code=200, success=True, message='Return info match', data="response_analysis")

    @app.route("/api/v1/plagiarism/disableHighlight", methods=['POST'])
    def disableHighlight():
        data = request.get_json()
        db = client.get_database(__collection__)
        collection = db.PlagiarismDetection
        responseCollection = collection.find({"_id":ObjectId(data['id'])})
        collection.update(
            { "_id":ObjectId(data['id']), "response_elastic.paragraph_text":data['text'] },
            { "$set": { 'response_elastic.$.status' : -1}}
        )
        list_cur = list(responseCollection)
        return jsonify(status_code=201, message='Report modify successfully!', data=list_cur)