from flask_unchained.bundles.controller import Controller, Resource, no_route, route


@route(endpoint='views.simple')
def simple():
    return 'simple'


@route(endpoint='views.one')
def one():
    return 'one'


@route(endpoint='views.two')
def two():
    return 'two'


@route(endpoint='views.three', methods=['GET', 'POST'])
def three():
    return 'three'


class SiteController(Controller):
    @route('/')
    def index(self):
        return self.render('index')

    def about(self):
        return self.render('about')

    def terms(self):
        return self.render('terms')

    def foobar(self):
        return self.render('foobar')


class ProductController(Controller):
    class Meta:
        url_prefix = '/products'

    @route('/')
    def index(self):
        return self.render('index')

    def good(self):
        return self.render('good')

    def better(self):
        return self.render('better')

    def best(self):
        return self.render('best')

    @no_route
    def not_a_route(self):
        return 'no leading underscore; needs to be decorated'

    @no_route()
    def also_not_a_route(self):
        return 'no leading underscore; needs to be decorated'

    def _private(self):
        return 'no route here!'


class UserResource(Resource):
    def list(self):
        return self.render('list')

    def create(self):
        return self.redirect('get', id=1)

    def get(self, id):
        return self.render('get', id=id)

    def put(self, id):
        return self.redirect('get', id=id)

    def patch(self, id):
        return self.redirect('get', id=id)

    def delete(self, id):
        return self.redirect('index')

    def foobar(self):
        return self.render('foobar')


class RoleResource(Resource):
    def list(self):
        return self.render('list')

    def create(self):
        return self.redirect('get', id=1)

    def get(self, id):
        return self.render('get', id=id)

    def put(self, id):
        return self.redirect('get', id=id)

    def patch(self, id):
        return self.redirect('get', id=id)

    def delete(self, id):
        return self.redirect('index')


class AnotherResource(Resource):
    class Meta:
        url_prefix = 'another'

    def list(self):
        return self.render('list')

    def get(self, id):
        return self.render('get', id=id)
