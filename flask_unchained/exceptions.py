class BundleNotFoundError(Exception):
    pass


class CWDImportError(ImportError):
    pass


class NameCollisionError(Exception):
    pass


class ServiceUsageError(Exception):
    pass


class UnchainedConfigNotFoundError(Exception):
    pass
