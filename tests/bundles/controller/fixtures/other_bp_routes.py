from flask_unchained.bundles.controller import func, include, prefix

from .bp_views import one, three, two


implicit = lambda: [
    func(one),
    func(two),
    func(three),
]

explicit = lambda: [
    func("/one", one),
    func("/two", two),
    func("/three", three),
]

recursive = lambda: [
    include("tests.bundles.controller.fixtures.other_bp_routes", attr="explicit"),
    prefix(
        "/deep",
        [include("tests.bundles.controller.fixtures.other_bp_routes", attr="implicit")],
    ),
]
