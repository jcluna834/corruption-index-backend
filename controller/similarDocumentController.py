__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from flask import request
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.similarDocument_dao import SimilarDocumentDAO
from settings import app, config
from flask import jsonify

class SimilarDocumentController(BaseController):
    similarDocument_dao: SimilarDocumentDAO = inject(SimilarDocumentDAO)

    def __init__(self):
        self.events = []

    '''
    @intercept()
    def get(self):
        """
        Fetches all the analyisHistory(paginated).
        :return:
        """
        res = self.similarDocument_dao.get_similarDocumento(page=int(request.args.get("page", 1)),
                                     per_page=int(request.args.get("per_page", 10)), all='all' in request.args)
        docs_info = dict(data=[d for d in res['data']], count=res['count'])
        return Response(data=docs_info)
    '''

    @app.route("/api/v1/plagiarism/getSimilarDocumentsInfo/", methods=['GET'])
    def getSimilarDocumentsInfo():
        documentID = request.args.get('documentID')
        document = SimilarDocumentController()
        res = document.similarDocument_dao.getSimilarDocumentsInfo(documentID)
        docs_info = dict(data=[d for d in res['data']], count=res['count'])
        return jsonify(status_code=200, message='Documents returned successfully!', data=docs_info)
