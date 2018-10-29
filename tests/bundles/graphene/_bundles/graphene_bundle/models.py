from flask_unchained.bundles.sqlalchemy import db


class Parent(db.Model):
    name = db.Column(db.String)

    children = db.relationship('Child', back_populates='parent',
                               cascade='all,delete,delete-orphan')


class Child(db.Model):
    name = db.Column(db.String)

    parent_id = db.foreign_key('Parent')
    parent = db.relationship('Parent', back_populates='children')
