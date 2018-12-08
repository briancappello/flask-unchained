import os

from flask_unchained import AppFactoryHook, Bundle


class DbFixtureDirsHook(AppFactoryHook):
    """

    """
    # we implement this hook only for fixtures folder name customization purposes

    bundle_module_name = 'fixtures'
    name = 'db_fixture_dirs'
    run_after = ['models']

    def run_hook(self, *args, **kwargs):
        pass  # noop

    @classmethod
    def get_fixtures_dir(cls, bundle: Bundle):
        folder_name = getattr(bundle,
                              cls.bundle_override_module_name_attr,
                              cls.bundle_module_name)
        if not folder_name:
            return None

        fixtures_dir = os.path.join(bundle.folder, folder_name)
        if not os.path.exists(fixtures_dir):
            return None

        return fixtures_dir
