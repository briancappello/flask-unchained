from flask_unchained.bundles.controller import func

from .views import silly_condition


routes = lambda: [
    func(silly_condition),
]
