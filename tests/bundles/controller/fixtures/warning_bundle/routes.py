from .views import silly_condition

from flask_unchained.bundles.controller import func


routes = [
    func(silly_condition),
]
