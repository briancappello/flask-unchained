from .admin import Admin


admin = Admin()


EXTENSIONS = {
    'admin': admin,
}


__all__ = [
    'admin',
    'Admin',
]
