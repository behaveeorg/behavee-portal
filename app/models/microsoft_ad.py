from app import db
from sqlalchemy import Text, Integer, DateTime


class Claims(db.Model):
    __bind_key__ = 'portal'
    id = db.Column(Integer(), primary_key=True, autoincrement=True)
    dt = db.Column(DateTime())
    claim = db.Column(Text())
    access_token = db.Column(Text())
