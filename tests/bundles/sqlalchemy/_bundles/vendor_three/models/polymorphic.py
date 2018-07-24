from flask_unchained.bundles.sqlalchemy import db


from .many_to_many_model import AssetDataVendor
from .many_to_many_table import index_equities


class Asset(db.Model):
    class Meta:
        polymorphic = True

    ticker = db.Column(db.String(16), index=True, unique=True)

    market_id = db.foreign_key('Market')
    market = db.relationship('Market', back_populates='assets')
    exchange = db.association_proxy('market', 'exchange')

    asset_data_vendors = db.relationship('AssetDataVendor',
                                         back_populates='asset',
                                         cascade='all, delete-orphan')
    data_vendors = db.association_proxy(
        'asset_data_vendors', 'data_vendor',
        creator=lambda data_vendor: AssetDataVendor(data_vendor=data_vendor))

    __repr_props__ = ('id', 'ticker')


class Equity(Asset):
    company_name = db.Column(db.String(64), index=True)

    indexes = db.relationship('Index', secondary=index_equities,
                              lazy='subquery', back_populates='equities')

    __repr_props__ = ('id', 'ticker', 'company_name')
