__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

import json
from model.base import BaseModel
from mysql_connector import db


class SimilarDocument(BaseModel):
    __tablename__ = 'similarDocument'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysisHistoryCode = db.Column('analysisHistoryCode', db.Integer, db.ForeignKey('analysisHistory.id'), nullable=False)
    analysisHistory = db.relationship("AnalysisHistory", backref=db.backref("analysisHistorySimilarDoc", uselist=False))

    documentCode = db.Column('documentCode', db.String(200), db.ForeignKey('documents.id'), nullable=False)
    document = db.relationship("Document", backref=db.backref("similarDocuments", uselist=False))

    status = db.Column('status', db.Integer, nullable=False)

    # Table metadata can be specified as follows -
    __table_args__ = (
        db.UniqueConstraint('analysisHistoryCode', 'documentCode'),
        db.Index(BaseModel.create_index(__tablename__, 'analysisHistoryCode', 'documentCode'), 'analysisHistoryCode', 'documentCode'),
    )

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'id': self.id,
            'documentCode': self.documentCode,
            'analysisHistoryCode': self.analysisHistoryCode,
            'status': self.status
        }