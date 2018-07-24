from .views import AdminDashboardView


class Config:
    ADMIN_NAME = 'Admin'
    ADMIN_BASE_URL = '/admin'
    ADMIN_INDEX_VIEW = AdminDashboardView()
    ADMIN_SUBDOMAIN = None
    ADMIN_BASE_TEMPLATE = 'admin/base.html'
    ADMIN_TEMPLATE_MODE = 'bootstrap3'
    ADMIN_CATEGORY_ICON_CLASSES = {}

    ADMIN_ROLE_ADMIN_NAME = 'ROLE_ADMIN'
    ADMIN_LOGIN_ENDPOINT = 'security.login'
    ADMIN_LOGOUT_ENDPOINT = 'security.logout'
    ADMIN_POST_LOGOUT_ENDPOINT = '/'


class TestConfig:
    TESTING = True
