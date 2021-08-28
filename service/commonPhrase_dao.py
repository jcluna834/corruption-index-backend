__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
from model import CommonPhrase
from math import ceil
from settings import config

class CommonPhraseDAO(BaseService):

    def getCurrentUser(self):
        return config['USERAUTHID']

    def getCurrentEntity(self):
        return config['ENTITYID']

    def yield_commonPhrases(self, page=1, per_page=10):
        """
        Yields a list of commonPhrase per page.
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

    def get_commonPhrases(self, announcementId, page=1, per_page=10, all=False):
        """
        Fetches commonPhrase' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of commonPhrase
        """
        start, stop = per_page * (page - 1), per_page * page
        query = {'is_deleted': 0, 'announcementCode': announcementId}

        doc_queryset = CommonPhrase.query.filter_by(**query)
        count = doc_queryset.count()
        doc_queryset = doc_queryset.order_by(CommonPhrase.created_date.desc())
        docs = doc_queryset.all() if all else doc_queryset.slice(start, stop).all()
        
        return {
            "data": docs,
            "count": count
        }

    def create_commonPhrase(self, description, phrase, announcementCode):
        """
        Creates an commonPhrase.
        :param data: commonPhrase's properties as json.
        :return:
        """
        commonPhrase = CommonPhrase(description=description, phrase=phrase, announcementCode=announcementCode)
        self.db.session.add(commonPhrase)
        self.db.session.commit()
        return commonPhrase

    def edit_commonPhrase(self, id, description, phrase):
        """
        Update an commonPhrase.
        :param data: commonPhrase's properties as json.
        :return:
        """
        announcement = CommonPhrase.query.filter_by(id=id).first()
        announcement.description = description
        announcement.phrase = phrase
        self.db.session.commit()
        return announcement

    def deleteCommonPhrase(self, commonPhraseId):
        deleted_objects = CommonPhrase.__table__.delete().where(CommonPhrase.id.in_([commonPhraseId]))
        self.db.session.execute(deleted_objects)
        self.db.session.commit()
