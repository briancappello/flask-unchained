from flask_unchained.bundles.sqlalchemy import db


class TwoBasic(db.Model):
    app = db.Column(db.String)
