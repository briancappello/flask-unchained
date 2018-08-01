from flask_unchained.bundles.controller import (
    controller, func, include, prefix, resource, rule)

from .bp_views import (SiteController, ProductController, simple,
                       UserResource, RoleResource, AnotherResource)


explicit_routes = lambda: [
    controller('/', SiteController, rules=[
        rule('/', 'index'),
        rule('/about', 'about'),
        rule('/terms', 'terms'),
    ]),
    resource('/users', UserResource, rules=[], subresources=[
        resource('/roles', RoleResource),
    ]),
    controller('/products', ProductController),
    func('/simple', simple),
    include('tests.bundles.controller.fixtures.other_bp_routes', attr='explicit'),
]

implicit_routes = lambda: [
    controller(SiteController),
    resource(UserResource, subresources=[
        resource(RoleResource),
    ]),
    prefix('/products', [
        controller(ProductController),
    ]),
    func(simple),
    include('tests.bundles.controller.fixtures.other_bp_routes', attr='implicit'),
]

deep = lambda: [
    prefix('/app', [
        controller('/site', SiteController),
        prefix('/pre', [
            resource(UserResource, subresources=[
                resource(RoleResource, subresources=[
                    # this deep of nesting is probably a bad idea,
                    # but it should work regardless
                    func(simple),
                    resource(AnotherResource),
                    include('tests.bundles.controller.fixtures.other_bp_routes', attr='recursive'),
                ]),
            ]),
        ]),
    ]),
]
