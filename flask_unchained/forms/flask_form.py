from flask_unchained.string_utils import snake_case
from flask_wtf import FlaskForm as BaseForm


class FlaskForm(BaseForm):
    """
    Base form class extending :class:`~flask_wtf.FlaskForm`. Adds support for
    specifying the field order via a ``field_order`` class attribute.
    """

    field_order = ()

    def __init__(self, formdata=None, obj=None, prefix='', data=None, meta=None,
                 **kwargs):
        """
        :param formdata:
            Used to pass data coming from the end user, usually `request.POST` or
            equivalent. formdata should be some sort of request-data wrapper which
            can get multiple parameters from the form input, and values are unicode
            strings, e.g. a Werkzeug/Django/WebOb MultiDict
        :param obj:
            If `formdata` is empty or not provided, this object is checked for
            attributes matching form field names, which will be used for field
            values.
        :param prefix:
            If provided, all fields will have their name prefixed with the
            value.
        :param data:
            Accept a dictionary of data. This is only used if `formdata` and
            `obj` are not present.
        :param meta:
            If provided, this is a dictionary of values to override attributes
            on this form's meta instance.
        :param `**kwargs`:
            If `formdata` is empty or not provided and `obj` does not contain
            an attribute named the same as a field, form will assign the value
            of a matching keyword argument to the field, if one exists.
        """
        super().__init__(formdata=formdata, obj=obj, prefix=prefix, data=data, meta=meta,
                         **kwargs)
        self._name = bytes(snake_case(self.__class__.__name__), 'utf-8')

    def __iter__(self):
        if not self.field_order:
            return super().__iter__()
        return iter([field for name, field in self._fields.items()
                     if name not in self.field_order]
                    + [self._fields[f] for f in self.field_order])
