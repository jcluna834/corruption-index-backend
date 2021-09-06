__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

import json
from model.base import BaseModel
from mysql_connector import db


class AnalysisHistory(BaseModel):
    __tablename__ = 'analysisHistory'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documentCode = db.Column('documentCode', db.String(200), db.ForeignKey('documents.id'), nullable=False)
    #historyDocumentAnalysis = db.relationship("Document", primaryjoin = "analysisHistory.documentCode == documents.id", backref=db.backref("documents", uselist=False))
    similarDocumentCode = db.Column('similarDocumentCode', db.String(200), db.ForeignKey('documents.id'), nullable=False)
    #historyDocumentSimilar = db.relationship("Document", primaryjoin = "analysisHistory.similarDocumentCode == documents.id", backref=db.backref("similarDocumentsHistory", uselist=False))
    status = db.Column('status', db.Integer, nullable=False)
    analysisTypeCode = db.Column('analysisTypeCode', db.Integer, nullable=False)
    collectionCode = db.Column('collectionCode', db.String(200))

    # Table metadata can be specified as follows -
    __table_args__ = (
        #db.UniqueConstraint('documentId', 'collectionId'),
        db.Index(BaseModel.create_index(__tablename__, 'documentCode', 'collectionCode'), 'documentCode', 'collectionCode'),
    )

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'id': self.id,
            'documentCode': self.documentCode,
            'collectionCode': self.collectionCode,
            'created_date': self.created_date.strftime("%m/%d/%Y, %H:%M:%S"),
            'status': self.status,
            'analysisTypeCode': self.analysisTypeCode
        }