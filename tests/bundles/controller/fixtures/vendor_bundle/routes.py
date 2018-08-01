from flask_unchained.bundles.controller import func

from .views import view_three, view_four


routes = lambda: [
    func(view_three),
    func(view_four),
]
