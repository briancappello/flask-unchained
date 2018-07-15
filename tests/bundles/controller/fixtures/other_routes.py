from flask_unchained.bundles.controller import func, prefix, include

from .views import one, two, three


implicit = [
    func(one),
    func(two),
    func(three),
]

explicit = [
    func('/one', one),
    func('/two', two),
    func('/three', three),
]

recursive = [
    include('tests.bundles.controller.fixtures.other_routes', attr='explicit'),
    prefix('/deep', [
        include('tests.bundles.controller.fixtures.other_routes', attr='implicit')
    ]),
]

routes = [
    func(one),
    func(two),
    func(three),
]
