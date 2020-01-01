from flask_unchained import AppFactoryHook


class ViewsHook(AppFactoryHook):
    """
    Allows configuring bundle views modules.
    """

    name = 'views'
    """
    The name of this hook.
    """

    bundle_module_names = ['views']
    """
    The default module this hook loads from.

    Override by setting the ``views_module_names`` attribute on your
    bundle class.
    """

    run_after = ['blueprints']

    def run_hook(self, app, bundles, unchained_config=None) -> None:
        pass  # noop
