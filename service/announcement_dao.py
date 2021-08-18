__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
from model import Announcement
from math import ceil
from settings import config

class AnnouncementDAO(BaseService):

    def getCurrentUser(self):
        return config['USERAUTHID']

    def getCurrentEntity(self):
        return config['ENTITYID']

    def yield_announcements(self, page=1, per_page=10):
        """
        Yields a list of announcements per page.
        :param page:
        :param per_page:
        :return:
        """
        announcements = self.get_announcements(page=page, per_page=per_page)
        iterations = ceil(announcements['count'] / per_page)

        yield announcements
        for _page in range(page + 1, iterations + 1):
            announcements = self.get_announcements(page=_page, per_page=per_page)
            yield announcements

    def get_announcements(self, page=1, per_page=10, all=False):
        """
        Fetches announcements' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of announcements
        """
        start, stop = per_page * (page - 1), per_page * page
        query = {'is_deleted': 0, 'responsible_code': self.getCurrentUser(), 'entity_code': self.getCurrentEntity()}

        doc_queryset = Announcement.query.filter_by(**query)
        count = doc_queryset.count()
        doc_queryset = doc_queryset.order_by(Announcement.created_date.desc())
        docs = doc_queryset.all() if all else doc_queryset.slice(start, stop).all()
        
        return {
            "data": docs,
            "count": count
        }

    def create_announcements(self, name, description, startDate, endDate, responsibleCode, entityCode):
        """
        Creates an announcements.
        :param data: announcements's properties as json.
        :return:
        """
        announcements = Announcement(name=name, description=description, startDate=startDate, endDate=endDate, responsible_code=responsibleCode, entity_code=entityCode)
        self.db.session.add(announcements)
        self.db.session.commit()
        return announcements

    def edit_announcements(self, id, name, description, startDate, endDate, responsibleCode, entityCode):
        """
        Update an announcements.
        :param data: announcements's properties as json.
        :return:
        """
        announcement = Announcement.query.filter_by(id=id).first()
        announcement.name = name
        announcement.description = description
        announcement.startDate = startDate
        announcement.endDate = endDate
        announcement.responsible_code = responsibleCode
        announcement.entity_code = entityCode
        self.db.session.commit()
        return announcement

    def deleteAnnouncement(self, announcementId):
        deleted_objects = Announcement.__table__.delete().where(Announcement.id.in_([announcementId]))
        self.db.session.execute(deleted_objects)
        self.db.session.commit()
