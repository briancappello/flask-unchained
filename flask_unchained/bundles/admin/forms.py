import sqlalchemy
from flask_admin.form import BaseForm
from flask_admin.form.fields import Select2Field
from flask_admin.model.form import converts
from flask_admin.contrib.sqla.form import AdminModelConverter as _BaseAdminModelConverter


class ReorderableForm(BaseForm):
    """
    Like :class:`~flask_admin.form.BaseForm`, except it supports re-ordering
    fields by setting the :attr:`field_order` class attribute to a list of
    field names.
    """

    def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
        super().__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if hasattr(self, 'field_order'):
            for field_name in self.field_order:
                self._fields.move_to_end(field_name)


class EnumField(Select2Field):
    """
    An extension of :class:`~flask_admin.form.fields.Select2Field`, adding support
    for :class:`~enum.Enum`.
    """

    def __init__(self, column, **kwargs):
        assert isinstance(column.type, sqlalchemy.sql.sqltypes.Enum)  # skipcq: BAN-B101

        def coercer(value):
            # coerce incoming value to enum value
            if isinstance(value, column.type.enum_class):
                return value
            elif isinstance(value, str):
                return column.type.enum_class[value]
            else:
                raise ValueError('Invalid choice {enum_class} {value}'.format(
                    enum_class=column.type.enum_class,
                    value=value
                ))

        super(EnumField, self).__init__(
            choices=[(v, v) for v in column.type.enums],
            coerce=coercer,
            **kwargs
        )

    def pre_validate(self, form):  # skipcq: PYL-W0613 (unused arg)
        for v, _ in self.choices:
            if self.data == self.coerce(v):
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))


class AdminModelFormConverter(_BaseAdminModelConverter):
    @converts('sqlalchemy.sql.sqltypes.Enum')
    def convert_enum(self, field_args, **extra):
        return EnumField(column=extra['column'], **field_args)
