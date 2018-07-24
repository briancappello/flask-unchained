from flask_admin import AdminIndexView as BaseAdminIndexView, expose

from ..security import AdminSecurityMixin


class AdminDashboardView(AdminSecurityMixin, BaseAdminIndexView):
    # overridden to not take any arguments
    def __init__(self):
        super().__init__()

    @expose('/')
    def index(self):
        return self.render('admin/dashboard.html')

    def is_visible(self):
        return False
