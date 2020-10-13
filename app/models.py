# -*- coding: utf-8 -*-
from app import app, db


class Users(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    telegram_id = db.Column(db.Integer())
    balance = db.Column(db.Float())

    def __repr__(self):
        return '<User: {}>'.format(self.id)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Ledger(db.Model):
    __tablename__ = 'Ledger'

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(80))
    guarantor = db.Column(db.String(80))
    amount = db.Column(db.Float())
    is_paid = db.Column(db.Boolean())
    date = db.Column(db.DateTime())

    def __repr__(self):
        return '<Ledger: {}>'.format(self.id)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)