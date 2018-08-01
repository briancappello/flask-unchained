from .views import silly_condition

from flask_unchained.bundles.controller import func


routes = lambda: [
    func(silly_condition),
]
