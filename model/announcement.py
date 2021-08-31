__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

import json
from model.base import BaseModel
from mysql_connector import db


class Announcement(BaseModel):
    __tablename__ = 'announcement'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(200), nullable=False)
    description = db.Column('description', db.Text(), nullable=False)
    startDate = db.Column('startDate', db.String(), nullable=False)
    endDate = db.Column('endDate', db.String(), nullable=False)
    responsible_code = db.Column('responsible_code', db.Integer, nullable=False)
    entity_code = db.Column('entity_code', db.Integer, nullable=False)

    # Table metadata can be specified as follows -
    __table_args__ = (
        db.UniqueConstraint('name', 'is_deleted'),
        db.Index(BaseModel.create_index(__tablename__, 'name', 'is_deleted'), 'name', 'is_deleted'),
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self, *args, **kwargs):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'startDate': self.startDate.strftime("%m/%d/%Y, %H:%M:%S"),
            'endDate': self.endDate.strftime("%m/%d/%Y, %H:%M:%S")
        }

    def to_dict_es(self, *args, **kwargs):
        return {
            'id': self.id,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'is_deleted': self.is_deleted,
            'name': self.name,
            'description': self.description,
            'startDate': self.startDate.strftime("%m/%d/%Y, %H:%M:%S"),
            'endDate': self.endDate.strftime("%m/%d/%Y, %H:%M:%S"),
            'entity_code': self.entity_code,
        }
