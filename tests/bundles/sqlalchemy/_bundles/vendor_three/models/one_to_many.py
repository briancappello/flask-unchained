from flask_unchained.bundles.sqlalchemy import db


class Exchange(db.Model):
    abbrev = db.Column(db.String(10), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)

    markets = db.relationship('Market', back_populates='exchange')

    __repr_props__ = ('id', 'abbrev', 'name')


class Market(db.Model):
    abbrev = db.Column(db.String(10), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)

    exchange_id = db.foreign_key('Exchange')
    exchange = db.relationship('Exchange', back_populates='markets')

    assets = db.relationship('Asset', back_populates='market')

    __repr_props__ = ('id', 'abbrev', 'name')
