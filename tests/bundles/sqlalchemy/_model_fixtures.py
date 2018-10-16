# import factory
# import pytest
#
# from flask_unchained.bundles.sqlalchemy import db
#
# from ._bundles.vendor_three.models import (
#     Basic, Timestamped, KeyedAndTimestamped,
#     User, UserProfile,
#     Asset, AssetDataVendor, DataVendor, Equity, Exchange, Index, Market)
#
#
# class AttrGetter:
#     def __init__(self, d):
#         self.d = d
#
#     def __getattr__(self, item):
#         return self.d[item]
#
#
# class ModelFactory(factory.Factory):
#     class Meta:
#         abstract = True
#
#     @classmethod
#     def _create(cls, model_class, *args, **kwargs):
#         filter_kwargs = {k: v for k, v in kwargs.items() if '__' not in k}
#         instance = model_class.get_by(**filter_kwargs)
#         if not instance:
#             instance = model_class(*args, **kwargs)
#             db.session.add(instance)
#             db.session.commit()
#         return instance
#
#
# class BasicFactory(ModelFactory):
#     class Meta:
#         model = Basic
#     name = 'basic'
#
#
# class TimestampedFactory(ModelFactory):
#     class Meta:
#         model = Timestamped
#     name = 'timestamped'
#
#
# class KeyedAndTimestampedFactory(ModelFactory):
#     class Meta:
#         model = KeyedAndTimestamped
#     name = 'keyed-and-timestamped'
#
#
# class UserProfileFactory(ModelFactory):
#     class Meta:
#         model = UserProfile
#     first_name = 'Wile E.'
#     last_name = 'Coyote'
#
#
# class UserFactory(ModelFactory):
#     class Meta:
#         model = User
#     username = 'username'
#     profile = factory.SubFactory(UserProfileFactory)
#
#
# class ExchangeFactory(ModelFactory):
#     class Meta:
#         model = Exchange
#     abbrev = 'NYSE'
#     name = 'New York Stock Exchange'
#
#
# class MarketFactory(ModelFactory):
#     class Meta:
#         model = Market
#     abbrev = 'NYSE'
#     name = 'New York Stock Exchange'
#     exchange = factory.SubFactory(ExchangeFactory)
#
#
# class DataVendorFactory(ModelFactory):
#     class Meta:
#         model = DataVendor
#     abbrev = 'yahoo'
#     name = 'Yahoo! Finance'
#
#
# class AssetFactory(ModelFactory):
#     class Meta:
#         model = Asset
#     ticker = 'ASSET'
#     market = factory.SubFactory(MarketFactory)
#
#
# class EquityFactory(AssetFactory):
#     class Meta:
#         model = Equity
#     ticker = 'ACME'
#     company_name = 'ACME Corporation'
#
#
# class AssetDataVendorFactory(ModelFactory):
#     class Meta:
#         model = AssetDataVendor
#     asset = factory.SubFactory(AssetFactory)
#     data_vendor = factory.SubFactory(DataVendorFactory)
#     ticker = None
#
#
# class EquityDataVendorFactory(AssetDataVendorFactory):
#     asset = factory.SubFactory(EquityFactory)
#
#
# class AssetWithDataVendorFactory(AssetFactory):
#     asset_data_vendor = factory.RelatedFactory(AssetDataVendorFactory, 'asset')
#
#
# class EquityWithDataVendorFactory(EquityFactory):
#     asset_data_vendor = factory.RelatedFactory(EquityDataVendorFactory, 'asset')
#
#
# @pytest.fixture()
# def basic(request):
#     kwargs = getattr(request.node.get_closest_marker('basic'), 'kwargs', {})
#     return BasicFactory(**kwargs)
#
#
# @pytest.fixture()
# def timestamped(request):
#     kwargs = getattr(request.node.get_closest_marker('timestamped'), 'kwargs', {})
#     return TimestampedFactory(**kwargs)
#
#
# @pytest.fixture()
# def keyed_and_timestamped(request):
#     kwargs = getattr(request.node.get_closest_marker('keyed_and_timestamped'), 'kwargs', {})
#     return KeyedAndTimestampedFactory(**kwargs)
#
#
# @pytest.fixture()
# def exchange(request):
#     kwargs = getattr(request.node.get_closest_marker('exchange'), 'kwargs', {})
#     return ExchangeFactory(**kwargs)
#
#
# @pytest.fixture()
# def market(request):
#     kwargs = getattr(request.node.get_closest_marker('market'), 'kwargs', {})
#     return MarketFactory(**kwargs)
#
#
# @pytest.fixture()
# def data_vendor(request):
#     kwargs = getattr(request.node.get_closest_marker('data_vendor'), 'kwargs', {})
#     return DataVendorFactory(**kwargs)
#
#
# @pytest.fixture()
# def asset(request):
#     kwargs = getattr(request.node.get_closest_marker('asset'), 'kwargs', {})
#     return AssetWithDataVendorFactory(**kwargs)
#
#
# @pytest.fixture()
# def equity(request):
#     kwargs = getattr(request.node.get_closest_marker('equity'), 'kwargs', {})
#     return EquityWithDataVendorFactory(**kwargs)
