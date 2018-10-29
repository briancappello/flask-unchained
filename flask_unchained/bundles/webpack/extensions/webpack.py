import json
import os

from flask import current_app
from flask_unchained import DEV
from markupsafe import Markup


class Webpack:
    """
    The ``Webpack`` extension::

        from flask_unchained.bundles.webpack import webpack
    """

    def __init__(self):
        self.assets = {}
        self.assets_host = None

    def init_app(self, app):
        # use relative paths by default, ie, the same host as the backend
        self.assets_host = app.config.get('WEBPACK_ASSETS_HOST', '')
        self._load_assets(app)

        if app.unchained.env == DEV:
            app.before_request(self._refresh_assets)
            if not self.assets_host:
                from warnings import warn
                warn('If you want HMR to work, you need to set '
                     'WEBPACK_ASSETS_HOST to point to your webpack-dev-server '
                     'address (http://localhost:3333 by default)')

        app.add_template_global(self.style_tag)
        app.add_template_global(self.script_tag)
        app.add_template_global(self.webpack_asset_url)

    def webpack_asset_url(self, asset):
        return self._url_for_asset(asset)

    def style_tag(self, href_or_bundle_name):
        href = self._url_for_asset(href_or_bundle_name, 'css')
        tag = f'<link rel="stylesheet" href="{href}">'
        return Markup(tag)

    def script_tag(self, src_or_bundle_name):
        src = self._url_for_asset(src_or_bundle_name, 'js')
        tag = f'<script src="{src}"></script>'
        return Markup(tag)

    def _load_assets(self, app):
        manifest_path = app.config.WEBPACK_MANIFEST_PATH
        if not manifest_path or not os.path.exists(manifest_path):
            return

        with open(manifest_path) as f:
            self.assets = json.load(f)

    def _refresh_assets(self):
        self._load_assets(current_app)

    def _url_for_asset(self, asset, bundle_type=None):
        if asset.startswith('/') or '://' in asset:
            return asset

        maybe_bundle_name = f'{asset}.{bundle_type}'
        if bundle_type == 'js':
            maybe_bundle_name = f'{asset}_js.{bundle_type}'
        if asset in self.assets:
            asset = self.assets[asset].lstrip('/')
        elif maybe_bundle_name in self.assets:
            asset = self.assets[maybe_bundle_name].lstrip('/')

        return f'{self.assets_host}/{asset}'
