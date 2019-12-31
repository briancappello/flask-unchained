from flask_unchained import AppFactoryHook


class ViewsHook(AppFactoryHook):
    """
    Allows configuring bundle views modules.
    """

    name = 'views'
    bundle_module_names = ['views']
    run_after = ['blueprints']

    def run_hook(self, app, bundles, unchained_config=None) -> None:
        pass  # noop
