from flask_admin import AdminIndexView as BaseAdminIndexView, expose

from ..security import AdminSecurityMixin


class AdminDashboardView(AdminSecurityMixin, BaseAdminIndexView):
    """
    Default admin dashboard view. Renders the ``admin/dashboard.html`` template.
    """

    # overridden to not take any arguments
    def __init__(self):
        super().__init__()

    @expose('/')
    def index(self):
        return self.render('admin/dashboard.html')

    def is_visible(self):
        """
        Overridden to hide this view from the menu by default.
        """
        return False
