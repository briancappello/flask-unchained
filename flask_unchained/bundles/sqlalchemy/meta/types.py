from collections import namedtuple


McsInitArgs = namedtuple('McsInitArgs', ('cls', 'name', 'bases', 'clsdict'))


class McsArgs:
    def __init__(self, mcs, name, bases, clsdict):
        self.mcs = mcs
        self.name = name
        self.bases = bases
        self.clsdict = clsdict

    @property
    def module(self):
        return self.clsdict.get('__module__')

    @property
    def model_repr(self):
        if self.module:
            return f'{self.module}.{self.name}'
        return self.name

    @property
    def model_meta(self):
        return self.clsdict['_meta']

    def __iter__(self):
        return iter([self.mcs, self.name, self.bases, self.clsdict])

    def __repr__(self):
        return f'<McsArgs model={self.model_repr}>'
