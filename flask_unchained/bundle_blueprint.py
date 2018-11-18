import os

from flask import Blueprint as _Blueprint, current_app
from flask.helpers import safe_join, send_file
from flask.blueprints import BlueprintSetupState as _BlueprintSetupState
from flask.helpers import _endpoint_from_view_func
from flask_unchained import Bundle
from werkzeug.exceptions import BadRequest, NotFound


class _BundleBlueprintSetupState(_BlueprintSetupState):
    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        A helper method to register a rule (and optionally a view function)
        to the application.  The endpoint is automatically prefixed with the
        blueprint's name.
        """
        if self.url_prefix:
            rule = self.url_prefix + rule
        options.setdefault('subdomain', self.subdomain)
        if endpoint is None:
            endpoint = _endpoint_from_view_func(view_func)
        defaults = self.url_defaults
        if 'defaults' in options:
            defaults = dict(defaults, **options.pop('defaults'))
        self.app.add_url_rule(rule, endpoint, view_func, defaults=defaults, **options)


class BundleBlueprint(_Blueprint):
    """
    This is a semi-private class to make blueprints compatible with bundles and
    their hierarchies. Bundle blueprints are created automatically for each bundle
    tht has a template folder and/or static folder. If *any* bundle in the hierarchy
    has views/routes that should be registered with the app, then those views/routes
    will get registered *only* with the :class:`BundleBlueprint` for the *top-most*
    bundle in the hierarchy.
    """
    url_prefix = None

    def __init__(self, bundle: Bundle):
        self.bundle = bundle
        super().__init__(bundle._blueprint_name, bundle.module_name,
                         static_url_path=bundle.static_url_path,
                         template_folder=bundle.template_folder)

    @property
    def has_static_folder(self):
        return bool(self.bundle._static_folders)

    def send_static_file(self, filename):
        if not self.has_static_folder:
            raise RuntimeError(f'No static folder found for {self.bundle.name}')
        # Ensure get_send_file_max_age is called in all cases.
        # Here, we ensure get_send_file_max_age is called for Blueprints.
        cache_timeout = self.get_send_file_max_age(filename)
        return _send_from_directories(self.bundle._static_folders, filename,
                                      cache_timeout=cache_timeout)

    def make_setup_state(self, app, options, first_registration=False):
        return _BundleBlueprintSetupState(self, app, options, first_registration)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        """
        Like :meth:`~flask.Flask.add_url_rule` but for a blueprint.  The endpoint for
        the :func:`url_for` function is prefixed with the name of the blueprint.

        Overridden to allow dots in endpoint names
        """
        self.record(lambda s: s.add_url_rule(rule, endpoint, view_func,
                                             register_with_babel=False, **options))

    def register(self, app, options, first_registration=False):
        """
        Called by :meth:`~flask.Flask.register_blueprint` to register a blueprint
        on the application.  This can be overridden to customize the register
        behavior.  Keyword arguments from
        :func:`~flask.Flask.register_blueprint` are directly forwarded to this
        method in the `options` dictionary.
        """
        self._got_registered_once = True
        state = self.make_setup_state(app, options, first_registration)
        if self.has_static_folder:
            state.add_url_rule(self.static_url_path + '/<path:filename>',
                               view_func=self.send_static_file,
                               endpoint=f'{self.bundle._blueprint_name}.static',
                               register_with_babel=False)

        for deferred in self.bundle._deferred_functions:
            deferred(self)

        for deferred in self.deferred_functions:
            deferred(state)

    def __repr__(self):
        return f'BundleBlueprint(name={self.name!r}, bundle={self.bundle!r})'


def _send_from_directories(directories, filename, **options):
    """
    Send a file from a given directory with :func:`send_file`.  This
    is a secure way to quickly expose static files from an upload folder
    or something similar.

    Example usage::

        @app.route('/uploads/<path:filename>')
        def download_file(filename):
            return send_from_directory(app.config.UPLOAD_FOLDER,
                                       filename, as_attachment=True)

    .. admonition:: Sending files and Performance

       It is strongly recommended to activate either ``X-Sendfile`` support in
       your webserver or (if no authentication happens) to tell the webserver
       to serve files for the given path on its own without calling into the
       web application for improved performance.

    :param directories: the list of directories to look for filename.
    :param filename: the filename relative to that directory to
                     download.
    :param options: optional keyword arguments that are directly
                    forwarded to :func:`send_file`.
    """
    for directory in directories:
        filename = safe_join(directory, filename)
        if not os.path.isabs(filename):
            filename = os.path.join(current_app.root_path, filename)
        try:
            if not os.path.isfile(filename):
                continue
        except (TypeError, ValueError):
            raise BadRequest()
        options.setdefault('conditional', True)
        return send_file(filename, **options)
    raise NotFound()


__all__ = [
    'BundleBlueprint',
]
