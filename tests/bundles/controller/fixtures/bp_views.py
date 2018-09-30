from flask import Blueprint

from flask_unchained.bundles.controller import Controller, Resource, route


bp = Blueprint('views', __name__, url_prefix='/bp')


@route(blueprint=bp)
def simple():
    return 'simple'


@route(blueprint=bp)
def one():
    return 'one'


@route(blueprint=bp)
def two():
    return 'two'


@route(blueprint=bp, methods=['GET', 'POST'])
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
    @route('/')
    def index(self):
        return self.render('index')

    def good(self):
        return self.render('good')

    def better(self):
        return self.render('better')

    @route
    def best(self):
        return self.render('best')


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
