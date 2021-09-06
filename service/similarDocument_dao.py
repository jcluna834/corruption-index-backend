__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
from model import SimilarDocument
from math import ceil
from settings import config
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import bindparam

class SimilarDocumentDAO(BaseService):


    def getSimilarDocumentsInfo(self, collectionID):
        """
        Fetches documents' list.
        :param docsID: id of documents
        :return: List of documents
        """

        stmt = text("select sd.id, d.id as documentId, d.title, d.description as documentDescription, a.id as announcementCode, "
            "a.name as announcementName, d.fileName, sd.status as similarDocStatus, ah2.collectionCode "
            "from analysishistory ah "
            "join documents d on ah.documentCode = d.id "
            "join announcement a on d.announcementCode = a.id "
            "join similardocument sd on d.id = sd.analysisDocumentCode "
            "left join analysishistory ah2 on sd.similarDocumentCode = ah2.similarDocumentCode "
            "where ah.collectionCode = :collectionCode").\
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

    def existsSimilarDoc(self, analysisDocumentCode, similarDocumentCode):
        """
        get especific document' .
        :param analysisDocumentCode
        :param similarDocumentCode
        :return: boll if exits similarDocument
        """
        query = {'analysisDocumentCode': analysisDocumentCode, 'similarDocumentCode':similarDocumentCode}
        exists = SimilarDocument.query.filter_by(**query).first() is not None
        return exists

    def createSimilarDocuments(self, analysisDocumentCode, similarDocumentCode, status=""):
        """
        Creates an analysisHistory.
        :param data: analysisHistory's properties as json.
        :return:
        """
        similarDocument = SimilarDocument(analysisDocumentCode=analysisDocumentCode, similarDocumentCode=similarDocumentCode, status=status)
        self.db.session.add(similarDocument)
        self.db.session.commit()
        return similarDocument

    def updateStatus(self, id, status):
        """
        Update an document.
        :param data: document's properties as json.
        :return:
        """
        document = SimilarDocument.query.filter_by(id=id).first()
        document.status = status
        self.db.session.commit()
        return document