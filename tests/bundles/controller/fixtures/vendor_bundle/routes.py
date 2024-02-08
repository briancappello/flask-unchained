from flask_unchained.bundles.controller import func

from .views import view_four, view_three


routes = lambda: [
    func(view_three),
    func(view_four),
]
