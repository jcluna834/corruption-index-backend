__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

from service.base import BaseService
from model import Document, Announcement
from math import ceil
from sqlalchemy.sql import text
from settings import config
from sqlalchemy.sql.expression import bindparam

class PlagiarismDAO(BaseService):

    def yield_docs(self, page=1, per_page=10):
        """
        Yields a list of documents per page.
        :param page:
        :param per_page:
        :return:
        """
        docs = self.get_docs(page=page, per_page=per_page)
        iterations = ceil(docs['count'] / per_page)

        yield docs
        for _page in range(page + 1, iterations + 1):
            docs = self.get_docs(page=_page, per_page=per_page)
            yield docs

    def get_docs(self, page=1, per_page=10, all=False):
        """
        Fetches documents' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of documents
        """

        start, stop = per_page * (page - 1), per_page * page
        query = {'is_deleted': 0}

        doc_queryset = Document.query.filter_by(**query)
        count = doc_queryset.count()
        doc_queryset = doc_queryset.order_by(Document.created_date.desc())
        docs = doc_queryset.all() if all else doc_queryset.slice(start, stop).all()

        return {
            "data": docs,
            "count": count
        }

    def get_docs_info(self, page=1, per_page=10, all=False):
        """
        Fetches documents' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of documents
        """
        start, stop = per_page * (page - 1), per_page * page
        query = {'is_deleted': 0}

        stmt = text("select d.id as documentId, d.title, d.description as documentDescription, a.id as announcementCode, a.name as announcementName, d.fileName, d.status "
            "from documents d join announcement a on d.announcementCode = a.id "
            "where d.is_deleted = 0 and a.is_deleted = 0 and d.responsibleCode = :codeUser and a.responsible_code = :codeUser "
            "order by d.title ").\
            bindparams(codeUser=config['USERAUTHID'])
            
        records = self.db.session.execute(stmt).fetchall()
        insertObject = []
        columnNames = [column for column in self.db.session.execute(stmt).keys()]
        for record in records:
            insertObject.append( dict( zip( columnNames , record ) ) )

        return {
            "data": insertObject,
            "count": len(records)
        }

    def getSimilarDocumentsInfo(self, docsID):
        """
        Fetches documents' list.
        :param docsID: id of documents
        :return: List of documents
        """
        print(docsID)
        params = { 'docs_id': docsID.split(','), }

        stmt = text("select d.id as documentId, d.title, d.description as documentDescription, a.id as announcementCode, a.name as announcementName, d.fileName, d.status "
            "from documents d join announcement a on d.announcementCode = a.id "
            "where d.id in :docs_id")
        stmt = stmt.bindparams(bindparam('docs_id', expanding=True))
        
        records = self.db.session.execute(stmt, params).fetchall()
        insertObject = []
        columnNames = [column for column in self.db.session.execute(stmt, params).keys()]
        for record in records:
            insertObject.append( dict( zip( columnNames , record ) ) )

        return {
            "data": insertObject,
            "count": len(records)
        }

    def get_doc(self, documentId):
        """
        get especific document' .
        :param id: Document id
        :return: List of documents
        """
        query = {'is_deleted': 0, 'id':documentId}
        doc_queryset = Document.query.filter_by(**query)
        docs = doc_queryset.one()
        return docs.to_dict_es()

    def get_doc_info(self, documentId):
        """
        get especific document' .
        :param id: Document id
        :return: List of documents
        """
        query = {'is_deleted': 0, 'id':documentId}
        doc_queryset = Document.query.filter_by(**query)
        docs = doc_queryset.one()
        return docs.to_dict()

    def existDocumentsAnnouncement(self, announcementId):
        """
        get documents' list fron annoumcement.
        :param id: Announcement id
        :return: List of documents
        """

        query = {'is_deleted': 0, 'announcementCode':announcementId}

        doc_queryset = Document.query.filter_by(**query)
        count = doc_queryset.count()
        doc_queryset = doc_queryset.order_by(Document.created_date.desc())
        docs = doc_queryset.all()

        return {
            "data": docs,
            "count": count
        }

    def create_doc(self, content, title, fileName, description='', responsibleCode='', announcementCode=''):
        """
        Creates an document.
        :param data: document's properties as json.
        :return:
        """
        doc = Document(content=content, title=title, 
            description=description, 
            responsibleCode=responsibleCode, announcementCode=announcementCode, 
            fileName=fileName, status=0)
        
        self.db.session.add(doc)
        self.db.session.commit()
        return doc

    def edit_doc(self, id, title, description='', responsibleCode='', announcementCode=''):
        """
        Update an document.
        :param data: document's properties as json.
        :return:
        """
        document = Document.query.filter_by(id=id).first()
        document.title = title
        document.description = description
        document.responsibleCode = responsibleCode
        document.announcementCode = announcementCode
        self.db.session.commit()
        return document

    def updateStatus(self, id, status):
        """
        Update an document.
        :param data: document's properties as json.
        :return:
        """
        document = Document.query.filter_by(id=id).first()
        document.status = status
        self.db.session.commit()
        return document
