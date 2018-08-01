from flask_unchained import controller, rule

from .views import AdminSecurityController


routes = lambda: [
    controller('/admin', AdminSecurityController, rules=[
        rule('/login', 'login', endpoint='admin.login'),
        rule('/logout', 'logout', endpoint='admin.logout'),
    ]),
]
