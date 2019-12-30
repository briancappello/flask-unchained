from flask_unchained.bundles.sqlalchemy import db


class Exchange(db.Model):
    class Meta:
        repr = ('id', 'abbrev', 'name')

    abbrev = db.Column(db.String(10), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)

    markets = db.relationship('Market', back_populates='exchange')


class Market(db.Model):
    class Meta:
        repr = ('id', 'abbrev', 'name')

    abbrev = db.Column(db.String(10), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)

    exchange_id = db.foreign_key('Exchange')
    exchange = db.relationship('Exchange', back_populates='markets')

    assets = db.relationship('Asset', back_populates='market')
