from flask_wtf import FlaskForm as BaseForm


class FlaskForm(BaseForm):
    """
    Base form class extending :class:`~flask_wtf.FlaskForm`. Adds support for
    specifying the field order via a ``field_order`` class attribute.
    """

    field_order = ()

    def __iter__(self):
        if not self.field_order:
            return super().__iter__()
        return iter([field for name, field in self._fields.items()
                     if name not in self.field_order]
                    + [self._fields[f] for f in self.field_order])
