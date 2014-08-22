# -*- coding: utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func, exc

from app import db

class Table(db.Model):
    __tablename__ = 'table'
    __table_args = {'mysql_engine': 'InnoDB'}

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), unique=True)

    created_at = db.Column(db.TIMESTAMP())
    updated_at = db.Column(db.TIMESTAMP(), server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))    

    def __init__(self, name=None):

        self.name = name

        if not self.created_at:
            self.created_at = dt.now()

    def __repr__(self):
        print u'<Table {id}>'.format(id=self.id)

    @classmethod
    def count(self):
        return db.session.query(func.count(self.id)).scalar()

"""
EOF
"""

