__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

from flask import request
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.plag_detector import PlagiarismDetector
from util.constants.error_codes import HttpErrorCode
from util.error_handlers.exceptions import ExceptionBuilder, BadRequest
from controller import elasticsearch
from controller import functions_plag
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

stopwords = stopwords.words('spanish')

class PlagiarismDetection(BaseController):
    plag_detector: PlagiarismDetector = inject(PlagiarismDetector)
    elasticsearhobj = elasticsearch.ElasticSearchFunction()
    functions_plag_obj = functions_plag.FunctionsPlagiarism()

    @intercept()
    def post(self, *args, **kwargs):
        """Detects plagiarism"""

        #response_skl = []
        response_es = []
        highlight_response = []
        data = request.get_json(force=True)
        input_doc = data.get('text', None)
        if input_doc is None:
            ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'text').throw()

        # Se divide en párrafos el texto recibido
        token_text = sent_tokenize(input_doc)
        for paragraph_text in token_text:
            ''' Se detecta similitud haciendo uso de sklearn
                Es omitido dado que se hará uso de ElasticSeach '''
            ''' most_similar_doc_info: Dict = self.plag_detector.compute_similarity(paragraph_text)
            most_similar_doc = most_similar_doc_info['doc']
            similarity_score = most_similar_doc_info['similarity_score']
            similarity_percentage = round(similarity_score * 100, 2)
            # Se arma la respuesta de sklearn
            res_data = {
                'paragraph_text': paragraph_text,
                'similarity_score': similarity_score,
                'similarity_percentage': similarity_percentage,
                'doc': most_similar_doc.to_dict()
            }
            response_skl.append(res_data) '''

            # Se detecta similitud haciendo uso de ElasticSearh
            responseES = self.elasticsearhobj.searchByContent(paragraph_text)
            # Se evalua cada párrafo retornado
            for highlight in responseES['hits']['hits'][0]['highlight']['content']:
                parag_text_clean = self.functions_plag_obj.getStringClean(paragraph_text)
                highlight_clean = self.functions_plag_obj.getStringClean(highlight)
                res_highlight_data = {
                    'content': highlight,
                    'levenshtein_distance': self.functions_plag_obj.getLevenshteinDistance(parag_text_clean, highlight_clean),
                    'similatiry_difflib': self.functions_plag_obj.getRatioSequenceMatcher(parag_text_clean, highlight_clean),
                    'uncommon_words': list(self.functions_plag_obj.getUncommonWords(parag_text_clean, highlight_clean))
                }
                highlight_response.append(res_highlight_data)

            # Se arma la respuesta a entregar en API
            res_es_data = {
                'paragraph_text': paragraph_text,
                'similarity_score': responseES['hits']['hits'][0]['_score'],
                'similarity_percentage': responseES['hits']['hits'][0]['_score'],
                'doc_': responseES['hits']['hits'][0]['_source'],
                'highlight': highlight_response
            }
            response_es.append(res_es_data)

        # Respuesta final entregada en el POST
        super_res_data = {
            'response_elastic': response_es
        }
        return Response(status_code=200, message='Return info match', data=super_res_data)