from flask_unchained.bundles.sqlalchemy import db


class DataVendor(db.Model):
    class Meta:
        repr = ('id', 'abbrev', 'name')

    abbrev = db.Column(db.String(10), index=True, unique=True)
    name = db.Column(db.String(64), index=True, unique=True)

    data_vendor_assets = db.relationship(
        'AssetDataVendor', back_populates='data_vendor')
    assets = db.association_proxy(
        'data_vendor_assets', 'asset',
        creator=lambda asset: AssetDataVendor(asset=asset))


class AssetDataVendor(db.Model):
    """Join table between Asset and DataVendor"""
    class Meta:
        repr = ('asset_id', 'data_vendor_id', 'ticker')

    asset_id = db.foreign_key('Asset', primary_key=True)
    asset = db.relationship('Asset', back_populates='asset_data_vendors')

    data_vendor_id = db.foreign_key('DataVendor', primary_key=True)
    data_vendor = db.relationship('DataVendor', back_populates='data_vendor_assets')

    # vendor-specific ticker (if different from canonical ticker on Asset)
    _ticker = db.Column('ticker', db.String(16), nullable=True)

    def __init__(self, asset=None, data_vendor=None, **kwargs):
        super().__init__(**kwargs)
        if asset:
            self.asset = asset
        if data_vendor:
            self.data_vendor = data_vendor

    @db.hybrid_property
    def ticker(self):
        return self._ticker or self.asset.ticker

    @ticker.setter
    def ticker(self, ticker):
        self._ticker = ticker
