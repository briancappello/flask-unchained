from flask_unchained.bundles.sqlalchemy import db


index_equities = db.Table(
    'index_equity',
    db.foreign_key('Index', column_name=True, primary_key=True),
    db.foreign_key('Equity', column_name=True, primary_key=True))


class Index(db.Model):
    name = db.Column(db.String(64), index=True, unique=True)
    ticker = db.Column(db.String(16), index=True, unique=True)

    equities = db.relationship('Equity', secondary=index_equities,
                               lazy='subquery', back_populates='indexes')
