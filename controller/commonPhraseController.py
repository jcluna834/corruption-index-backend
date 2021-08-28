__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from flask import request
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.commonPhrase_dao import CommonPhraseDAO
from service.plag_dao import PlagiarismDAO
from util.constants.error_codes import HttpErrorCode
from util.error_handlers.exceptions import ExceptionBuilder, BadRequest
import json
from settings import app, config
from flask import jsonify

class CommonPhraseController(BaseController):
    commonPhrase_dao: CommonPhraseDAO = inject(CommonPhraseDAO)
    plag_dao: PlagiarismDAO = inject(PlagiarismDAO)

    def __init__(self):
        self.events = []

    def saveCommonPhrase(self, data, option):
        description = data.get('description', '')
        phrase = data.get('phrase', '')
        announcementCode = data.get('announcementCode', '')
        if phrase and description:
            # Se agrega el documento en la BD
            if (option == "save"):
                if(announcementCode):
                    self.commonPhrase_dao.create_commonPhrase(description, phrase, announcementCode)
                else:
                    ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'announcementCode').throw()
            else:
                id = data.get('id', '')
                self.commonPhrase_dao.edit_commonPhrase(id, description, phrase)
        else:
            ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'phrase', 'descripction').throw()

        return Response(status_code=201, message='Common Phrase ' + option + 'd successfully!')

    @intercept()
    def get(self):
        announcementCode = request.args.get('announcementCode')
        """
        Fetches all the CommonPhrases(paginated).
        :return:
        """
        res = self.commonPhrase_dao.get_commonPhrases(announcementId = announcementCode, page=int(request.args.get("page", 1)),
                                     per_page=int(request.args.get("per_page", 10)), all='all' in request.args)
        docs_info = dict(data=[d.to_dict() for d in res['data']], count=res['count'])
        return Response(data=docs_info)

    @intercept()
    def post(self, *args, **kwargs):
        data = request.get_json(force=True)
        return self.saveCommonPhrase(data, "save")

    @intercept()
    def put(self, *args, **kwargs):
        data = request.get_json(force=True)
        return self.saveCommonPhrase(data, "update")

    
    @intercept()
    def delete(self, *args, **kwargs):
        try:
            id = request.get_json()
            self.commonPhrase_dao.deleteCommonPhrase(id)
        except:
            return Response(status_code=500, message='Error to delete Common Phrase!')
        return Response(status_code=201, message='Common Phrase deleted successfully!')
