__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
from model import AnalysisHistory
from math import ceil
from settings import config
from sqlalchemy.sql import text

class AnalysisHistoryDAO(BaseService):


    def yield_announcements(self, page=1, per_page=10):
        """
        Yields a list of announcements per page.
        :param page:
        :param per_page:
        :return:
        """
        analysisHistory = self.get_analysisHistory(page=page, per_page=per_page)
        iterations = ceil(analysisHistory['count'] / per_page)

        yield analysisHistory
        for _page in range(page + 1, iterations + 1):
            analysisHistory = self.get_analysisHistory(page=_page, per_page=per_page)
            yield analysisHistory

    def get_analysisHistory(self, page=1, per_page=10, all=False):
        """
        Fetches analysisHistory' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of analysisHistory
        """
        start, stop = per_page * (page - 1), per_page * page
        query = {'is_deleted': 0, 'status': 0}

        doc_queryset = AnalysisHistory.query.filter_by(**query)
        count = doc_queryset.count()
        doc_queryset = doc_queryset.order_by(AnalysisHistory.created_date.desc())
        docs = doc_queryset.all() if all else doc_queryset.slice(start, stop).all()
        return {
            "data": docs,
            "count": count
        }

    def get_analysisHistory_info(self, page=1, per_page=10, all=False):
        """
        Fetches documents' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of documents
        """
        start, stop = per_page * (page - 1), per_page * page
        query = {'is_deleted': 0}

        stmt = text("select a.id, a.documentCode, a.collectionCode, a.status, DATE_FORMAT(a.created_date, '%d/%m/%y %T') as created_date, "
            "d.title, an.name as announcementName, at.name as AnalysisType, at.description as AnalysisTypeDesc "
            "from analysishistory a  "
            "join documents d on a.documentCode = d.id  "
            "join announcement an on d.announcementCode = an.id "
            "join analysistype at on a.analysisTypeCode = at.id "
            "where a.is_deleted = 0 and a.status = 0")
            
        records = self.db.session.execute(stmt).fetchall()
        insertObject = []
        columnNames = [column for column in self.db.session.execute(stmt).keys()]
        for record in records:
            insertObject.append( dict( zip( columnNames , record ) ) )

        return {
            "data": insertObject,
            "count": len(records)
        }

    def analysisHistoryByCollectionCode(self, collectionID):
        """
        Fetches documents' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of documents
        """

        stmt = text("select a.id, a.documentCode, a.collectionCode, a.status, DATE_FORMAT(a.created_date, '%d/%m/%y %T') as created_date, "
            "d.title, an.name as announcementName, at.id as AnalysisTypeID, at.name as AnalysisType, at.description as AnalysisTypeDesc "
            "from analysishistory a  "
            "join documents d on a.documentCode = d.id  "
            "join announcement an on d.announcementCode = an.id "
            "join analysistype at on a.analysisTypeCode = at.id "
            "where a.is_deleted = 0 and a.status = 1 and a.collectionCode=:collectionCode").\
            bindparams(collectionCode=collectionID)
            
        records = self.db.session.execute(stmt).fetchall()
        insertObject = []
        columnNames = [column for column in self.db.session.execute(stmt).keys()]
        for record in records:
            insertObject.append( dict( zip( columnNames , record ) ) )

        return {
            "data": insertObject,
            "count": len(records)
        }

    def analysisHistoryByDocumentCode(self, documentID):
        """
        Fetches documents' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of documents
        """

        stmt = text("select a.id, a.documentCode, a.collectionCode, a.status, DATE_FORMAT(a.created_date, '%d/%m/%y %T') as created_date, "
            "d.title, an.name as announcementName, at.name as AnalysisType, at.description as AnalysisTypeDesc "
            "from analysishistory a  "
            "join documents d on a.documentCode = d.id  "
            "join announcement an on d.announcementCode = an.id "
            "join analysistype at on a.analysisTypeCode = at.id "
            "where a.is_deleted = 0 and a.status = 1 and a.documentCode=:documentCode").\
            bindparams(documentCode=documentID)
            
        records = self.db.session.execute(stmt).fetchall()
        insertObject = []
        columnNames = [column for column in self.db.session.execute(stmt).keys()]
        for record in records:
            insertObject.append( dict( zip( columnNames , record ) ) )

        return {
            "data": insertObject,
            "count": len(records)
        }

    def create_analysisHistory(self, documentId, status, analysisType, collectionId=""):
        """
        Creates an analysisHistory.
        :param data: analysisHistory's properties as json.
        :return:
        """
        analysisHistory = AnalysisHistory(documentCode=documentId, status=status, analysisTypeCode=analysisType, collectionCode=collectionId)
        self.db.session.add(analysisHistory)
        self.db.session.commit()
        return analysisHistory

    def edit_analysisHistory(self, id, status, collectionId):
        """
        Update an announcements.
        :param data: announcements's properties as json.
        :return:
        """

        analysisHistory = AnalysisHistory.query.filter_by(id=id).first()
        analysisHistory.status = status
        analysisHistory.collectionCode = collectionId
        self.db.session.commit()
        return analysisHistory

    def changeStatus(self, id, status):
        """
        Update an announcements.
        :param data: announcements's properties as json.
        :return:
        """
        analysisHistory = AnalysisHistory.query.filter_by(id=id).first()
        analysisHistory.status = status
        self.db.session.commit()
        return analysisHistory