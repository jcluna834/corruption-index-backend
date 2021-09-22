__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from flask import request, flash, redirect, url_for
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.announcement_dao import AnnouncementDAO
from service.plag_dao import PlagiarismDAO
from util.constants.error_codes import HttpErrorCode
from util.error_handlers.exceptions import ExceptionBuilder, BadRequest
from controller import elasticsearch
import json
from settings import app, config
from flask import jsonify

class Announcement(BaseController):
    announcement_dao: AnnouncementDAO = inject(AnnouncementDAO)
    elasticsearhobj = elasticsearch.ElasticSearchFunction()
    plag_dao: PlagiarismDAO = inject(PlagiarismDAO)

    def __init__(self):
        self.events = []

    def saveAnnouncement(self, data, option):
        name = data.get('name', '')
        description = data.get('description', '')
        startDate = data.get('startDate', '')
        endDate = data.get('endDate', '')
        responsible_code = data.get('responsibleCode', '')
        entity_code = data.get('entityCode', '')
        if name and description and endDate and startDate:
            # Se agrega el documento en la BD
            if (option == "save"):
                self.announcement_dao.create_announcements(name, description, startDate, endDate, responsible_code, entity_code)
            else:
                id = data.get('id', '')
                self.announcement_dao.edit_announcements(id, name, description, startDate, endDate, responsible_code, entity_code)
        else:
            ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'name').throw()

        return Response(status_code=201, message='Announcement added successfully!')

    @intercept()
    def post(self, *args, **kwargs):
        """Adds a new document to repo"""
        data = request.get_json(force=True)
        return self.saveAnnouncement(data, "save")

    @intercept()
    def get(self):
        """
        Fetches all the documents(paginated).
        :return:
        """
        res = self.announcement_dao.get_announcements(page=int(request.args.get("page", 1)),
                                    per_page=int(request.args.get("per_page", 10)), all='all' in request.args)
        docs_info = dict(data=[d.to_dict() for d in res['data']], count=res['count'])
        return Response(data=docs_info)

    @intercept()
    def delete(self, *args, **kwargs):
        try:
            id = request.get_json()
            res = self.plag_dao.existDocumentsAnnouncement(id)
            if(res['count'] > 0):
                return Response(success=False, status_code=200, message='Announcement cant be deleted because has documents!')
            
            self.announcement_dao.deleteAnnouncement(id)
        except:
            return Response(status_code=500, message='Error to delete Announcement!')
        return Response(status_code=201, message='Announcement deleted successfully!')

    @intercept()
    def put(self, *args, **kwargs):
        """Adds a new document to repo"""
        data = request.get_json(force=True)
        return self.saveAnnouncement(data, "update")
