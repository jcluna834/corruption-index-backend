__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

import json
from model.base import BaseModel
from mysql_connector import db


class CommonPhrase(BaseModel):
    __tablename__ = 'commonPhrase'

    description = db.Column('description', db.String(200), nullable=False)
    phrase = db.Column('phrase', db.Text(), nullable=False)
    announcementCode = db.Column('announcementCode', db.Integer, db.ForeignKey('announcement.id'), nullable=False)
    announcement = db.relationship("Announcement", backref=db.backref("announcement", uselist=False))
    

    # Table metadata can be specified as follows -
    __table_args__ = (
        db.Index(BaseModel.create_index(__tablename__, 'announcementCode'), 'announcementCode'),
    )

    def __str__(self):
        return self.title

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'id': self.id,
            'description': self.description,
            'phrase': self.phrase,
            'announcementCode': self.announcementCode,
            'announcement': self.announcement.to_dict()
        }