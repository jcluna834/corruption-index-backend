__author__ = "Suyash Soni"
__email__ = "suyash.soni248@gmail.com"

import json
from model.base import BaseModel
from mysql_connector import db


class Document(BaseModel):
    __tablename__ = 'documents'

    content = db.Column('content', db.Text(), nullable=False)
    title = db.Column('title', db.String(200), nullable=False)
    fileName = db.Column('fileName', db.String(200), nullable=False)
    description = db.Column('description', db.Text(), nullable=False)
    responsibleCode = db.Column('responsibleCode', db.Integer, nullable=False)
    announcementCode = db.Column('announcementCode', db.Integer, nullable=False)
    status = db.Column('status', db.Integer, nullable=False)

    # Table metadata can be specified as follows -
    __table_args__ = (
        db.UniqueConstraint('title', 'is_deleted'),
        db.Index(BaseModel.create_index(__tablename__, 'title', 'is_deleted'), 'title', 'is_deleted'),
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'fileName': self.fileName,
            'announcementCode': self.announcementCode
        }

    def to_dict_es(self, *args, **kwargs):
        return {
            'id': self.id,
            'created_date': self.created_date,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'responsibleCode': self.responsibleCode,
            'announcementCode': self.announcementCode,
            'is_deleted': self.is_deleted
        }
