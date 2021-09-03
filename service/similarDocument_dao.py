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
            "a.name as announcementName, d.fileName, sd.status as similarDocStatus "
            "from similardocument sd  "
            "join documents d on sd.similarDocumentCode = d.id "
            "join announcement a on d.announcementCode = a.id  "
            "join analysishistory ah on sd.analysisHistoryCode = ah.id  "
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