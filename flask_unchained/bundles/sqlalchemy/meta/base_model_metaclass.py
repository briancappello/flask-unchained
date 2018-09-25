import re

from collections import defaultdict
from py_meta_utils import McsArgs, deep_getattr
from sqlalchemy import Column
from sqlalchemy_unchained import DeclarativeMeta

VALIDATOR_RE = re.compile(r'^validates?_(?P<column>\w+)')


class BaseModelMetaclass(DeclarativeMeta):
    def _pre_mcs_new(cls, mcs_args: McsArgs):
        _, name, bases, clsdict = mcs_args
        validators = deep_getattr(clsdict, bases, '__validators__', defaultdict(list))
        columns = {col_name: col for col_name, col in clsdict.items()
                   if isinstance(col, Column)}
        for col_name, col in columns.items():
            if not col.name:
                col.name = col_name
            if col.info:
                for v in col.info.get('validators', []):
                    if v not in validators[col_name]:
                        validators[col_name].append(v)

        for attr_name, attr in clsdict.items():
            validates = getattr(attr, '__validates__', None)
            if validates and deep_getattr(clsdict, mcs_args.bases, validates):
                if attr_name not in validators[attr.__validates__]:
                    validators[attr.__validates__].append(attr_name)
                continue

            m = VALIDATOR_RE.match(attr_name)
            column = m.groupdict()['column'] if m else None
            if m and deep_getattr(clsdict, mcs_args.bases, column, None) is not None:
                attr.__validates__ = column
                if attr_name not in validators[column]:
                    validators[column].append(attr_name)
        clsdict['__validators__'] = validators
