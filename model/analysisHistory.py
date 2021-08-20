__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

import json
from model.base import BaseModel
from mysql_connector import db


class AnalysisHistory(BaseModel):
    __tablename__ = 'analysisHistory'

    documentCode = db.Column('documentCode', db.String(200), db.ForeignKey('documents.id'), nullable=False)
    document = db.relationship("Document", backref=db.backref("documents", uselist=False))
    status = db.Column('status', db.Integer, nullable=False)
    collectionCode = db.Column('collectionCode', db.String(200))

    # Table metadata can be specified as follows -
    __table_args__ = (
        #db.UniqueConstraint('documentId', 'collectionId'),
        db.Index(BaseModel.create_index(__tablename__, 'documentCode', 'collectionCode'), 'documentCode', 'collectionCode'),
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'id': self.id,
            'documentCode': self.documentCode,
            'collectionCode': self.collectionCode,
            'created_date': self.created_date.strftime("%m/%d/%Y, %H:%M:%S"),
            'status': self.status
        }