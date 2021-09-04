__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

import json
from model.base_init import BaseInitModel
from mysql_connector import db
from settings import config


class SimilarDocument(BaseInitModel):
    __tablename__ = 'similarDocument'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysisHistoryCode = db.Column('analysisHistoryCode', db.Integer, db.ForeignKey('analysisHistory.id'), nullable=False)
    analysisHistory = db.relationship("AnalysisHistory", backref=db.backref("analysisHistorySimilarDoc", uselist=False))

    similarDocumentCode = db.Column('similarDocumentCode', db.String(200), db.ForeignKey('documents.id'), nullable=False)
    document = db.relationship("Document", backref=db.backref("similarDocuments", uselist=False))

    status = db.Column('status', db.Integer, nullable=False)

    # Table metadata can be specified as follows -
    __table_args__ = (
        db.UniqueConstraint('analysisHistoryCode', 'similarDocumentCode'),
        db.Index(BaseInitModel.create_index(__tablename__, 'analysisHistoryCode', 'similarDocumentCode'), 'analysisHistoryCode', 'similarDocumentCode'),
    )

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'id': self.id,
            'similarDocumentCode': self.similarDocumentCode,
            'analysisHistoryCode': self.analysisHistoryCode,
            'status': self.status
        }
