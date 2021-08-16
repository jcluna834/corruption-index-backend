__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from flask import request, flash, redirect, url_for
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.announcement_dao import AnnouncementDAO
from util.constants.error_codes import HttpErrorCode
from util.error_handlers.exceptions import ExceptionBuilder, BadRequest
from controller import elasticsearch
import json
from settings import app, config
from flask import jsonify

class Announcement(BaseController):
    announcement_dao: AnnouncementDAO = inject(AnnouncementDAO)
    elasticsearhobj = elasticsearch.ElasticSearchFunction()

    def __init__(self):
        self.events = []

    def saveAnnouncement(self, data):
        name = data.get('name', '')
        description = data.get('description', '')
        startDate = data.get('startDate', '')
        endDate = data.get('endDate', '')
        responsible_code = data.get('responsibleCode', '')
        entity_code = data.get('entityCode', '')
        if name and description:
            # Se agrega el documento en la BD
            self.announcement_dao.create_announcements(name, description, startDate, endDate, responsible_code, entity_code)
        else:
            ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'name').throw()

        return Response(status_code=201, message='Announcement added successfully!')

    @intercept()
    def post(self, *args, **kwargs):
        """Adds a new document to repo"""
        data = request.get_json(force=True)
        return self.saveAnnouncement(data)

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
