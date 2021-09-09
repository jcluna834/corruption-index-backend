__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

import json
from model.base_init import BaseInitModel
from mysql_connector import db
from settings import config


class SimilarDocument(BaseInitModel):
    __tablename__ = 'similarDocument'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysisDocumentCode = db.Column('analysisDocumentCode', db.String(200), db.ForeignKey('documents.id'), nullable=False)
    #similarDocumentAnalysis = db.relationship("Document",  foreign_keys=["analysisDocumentCode"], backref=db.backref("analysisDocumentCode", uselist=False))
    similarDocumentCode = db.Column('similarDocumentCode', db.String(200), db.ForeignKey('documents.id'), nullable=False)
    #similarDocumentSimilar = db.relationship("Document", foreign_keys=["similarDocumentCode"], backref=db.backref("similarDocuments", uselist=False))

    status = db.Column('status', db.Integer, nullable=False)

    # Table metadata can be specified as follows -
    __table_args__ = (
        db.UniqueConstraint('analysisDocumentCode', 'similarDocumentCode'),
        db.Index(BaseInitModel.create_index(__tablename__, 'analysisDocumentCode', 'similarDocumentCode'), 'analysisDocumentCode', 'similarDocumentCode'),
    )

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'id': self.id,
            'analysisDocumentCode': self.analysisDocumentCode,
            'similarDocumentCode': self.similarDocumentCode,
            'status': self.status
        }
