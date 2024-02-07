from flask_unchained.string_utils import snake_case
from flask_wtf.form import FlaskForm as BaseForm, _Auto
from wtforms import FileField as _FileField, SubmitField as _SubmitField


class FlaskForm(BaseForm):
    """
    Base form class extending :class:`flask_wtf.FlaskForm`. Adds support for
    specifying the field order via a ``field_order`` class attribute.

    :param formdata: Used to pass data coming from the end user, usually
                     ``request.POST`` or equivalent. formdata should be some
                     sort of request-data wrapper which can get multiple
                     parameters from the form input, and values are unicode
                     strings, e.g. a Werkzeug/Django/WebOb MultiDict
    :param obj: If ``formdata`` is empty or not provided, this object is
                checked for attributes matching form field names, which will
                be used for field values.
    :param prefix: If provided, all fields will have their name prefixed with
                   the value.
    :param data: Accept a dictionary of data. This is only used if ``formdata``
                 and `obj` are not present.
    :param meta: If provided, this is a dictionary of values to override
                 attributes on this form's meta instance.
    :param `**kwargs`: If `formdata` is empty or not provided and `obj` does
                       not contain an attribute named the same as a field,
                       form will assign the value of a matching keyword
                       argument to the field, if one exists.
    """

    field_order = ()
    """
    An ordered list of field names. Fields not listed here will be rendered last.
    """

    submit = _SubmitField("Submit")

    def __init__(
        self, formdata=_Auto, obj=None, prefix="", data=None, meta=None, **kwargs
    ):
        super().__init__(
            formdata=formdata, obj=obj, prefix=prefix, data=data, meta=meta, **kwargs
        )
        self._name = snake_case(self.__class__.__name__)
        self._enctype = "application/x-www-form-urlencoded"
        for field in self._fields.values():
            if isinstance(field, _FileField):
                self._enctype = "multipart/form-data"

    def __iter__(self):
        """
        Overridden to always return the submit fields last (unless their
        order is explicitly set in :attr:`field_order`)
        """
        name = None
        try:
            fields = [self._fields[name] for name in self.field_order]
        except KeyError as e:
            raise RuntimeError(
                f"{str(e)} is listed in `field_order` but the " f"field is not defined"
            )
        extra_fields = []
        submit_fields = {}

        for name, field in self._fields.items():
            if isinstance(field, _SubmitField):
                submit_fields[name] = field
            elif name not in self.field_order:
                extra_fields.append(field)

        if submit_fields:
            for name, field in submit_fields.items():
                if name not in self.field_order:
                    extra_fields.append(field)

        return iter(fields + extra_fields)
