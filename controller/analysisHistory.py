__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from flask import request
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.analysisHistory_dao import AnalysisHistoryDAO
from settings import app, config
from flask import jsonify

class AnalysisHistory(BaseController):
    analyisHistory_dao: AnalysisHistoryDAO = inject(AnalysisHistoryDAO)

    def __init__(self):
        self.events = []

    @intercept()
    def get(self):
        """
        Fetches all the analyisHistory(paginated).
        :return:
        """
        res = self.analyisHistory_dao.get_analysisHistory_info(page=int(request.args.get("page", 1)),
                                    per_page=int(request.args.get("per_page", 10)), all='all' in request.args)
        docs_info = dict(data=[d for d in res['data']], count=res['count'])
        return Response(data=docs_info)

    @app.route("/api/v1/plagiarism/getReportAnalysis/<collectionID>", methods=['GET'])
    def getReportAnalysis(collectionID):
        analysisHistoryController = AnalysisHistory()
        analysisHistory = analysisHistoryController.analyisHistory_dao.analysisHistoryByCollectionCode(collectionID)
        return jsonify(status_code=201, message='Reports returned successfully!', data=analysisHistory)

    def cleanAnalysisHistory():
        analysisHistoryController = AnalysisHistory()
        analysisHistoryController.analyisHistory_dao.cleanAnalysisHistory()