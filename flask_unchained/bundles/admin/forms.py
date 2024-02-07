import re

from datetime import timedelta

from flask_admin import form as admin_form
from flask_admin.form import fields as admin_fields
from flask_admin.model.form import converts
from flask_admin.contrib.sqla.form import (
    AdminModelConverter as _BaseAdminModelConverter,
)

from wtforms import Field, fields, widgets


DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = f"{DATE_FORMAT} %I:%M%p %z"


class ReorderableForm(admin_form.BaseForm):
    """
    Like :class:`~flask_admin.form.BaseForm`, except it supports re-ordering
    fields by setting the :attr:`field_order` class attribute to a list of
    field names.
    """

    def __init__(self, formdata=None, obj=None, prefix="", **kwargs):
        super().__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        if hasattr(self, "field_order"):
            for field_name in self.field_order:
                self._fields.move_to_end(field_name)


def _set_data_date_format_render_kw(kwargs):
    # from strptime
    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    # to momentjs
    # https://momentjs.com/docs/#/displaying/format/
    substitutes = {
        "%a": "ddd",
        "%A": "dddd",
        "%w": "d",
        "%d": "DD",
        "%-d": "D",
        "%b": "MMM",
        "%B": "MMMM",
        "%m": "MM",
        "%-m": "M",
        "%y": "YY",
        "%Y": "Y",
        "%H": "HH",
        "%-H": "H",
        "%I": "hh",
        "%-I": "h",
        "%p": "A",
        "%M": "mm",
        "%-M": "m",
        "%S": "ss",
        "%-S": "s",
        "%z": "ZZ",
        "%Z": "z",
        "%j": "DDDD",
        "%U": "ww",
        "%-U": "w",
        "%W": "WW",
        "%-W": "W",
    }
    kwargs.setdefault("render_kw", {}).setdefault(
        "data-date-format",
        re.sub(r"%-?\w", lambda m: substitutes[m[0]], kwargs["format"]),
    )
    return kwargs


class DateField(fields.DateField):
    widget = admin_form.DatePickerWidget()

    def __init__(
        self,
        label=None,
        validators=None,
        format=DATE_FORMAT,
        **kwargs,
    ):
        kwargs = _set_data_date_format_render_kw(dict(**kwargs, format=format))
        super().__init__(label, validators, **kwargs)


class DateTimeField(admin_fields.DateTimeField):
    def __init__(
        self,
        label=None,
        validators=None,
        format=DATETIME_FORMAT,
        **kwargs,
    ):
        kwargs = _set_data_date_format_render_kw(dict(**kwargs, format=format))
        super().__init__(label, validators, **kwargs)


class IntervalField(Field):
    widget = widgets.TextInput()
    duration_regex = re.compile(r"(?P<duration>\d+(?:\.\d+)?)\s?(?P<unit>\w+)")

    def _value(self):
        if not self.data:
            return ""
        return self.timedelta_to_string(self.data)

    def process_formdata(self, valuelist):
        if not valuelist:
            self.data = timedelta()
        else:
            self.data = self.string_to_timedelta(valuelist[0])

    @staticmethod
    def timedelta_to_string(td):
        minutes, seconds = divmod(td.total_seconds(), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        pairs = [
            (days, "days"),
            (hours, "hours"),
            (minutes, "minutes"),
            (seconds, "seconds"),
        ]
        amounts = [
            (
                (str(int(amount)), unit)
                if divmod(amount, 1)[1] == 0
                else (f"{float(amount)}:.2f", unit)
            )
            for amount, unit in pairs
            if amount
        ]
        return ", ".join(f"{amount} {unit}" for amount, unit in amounts)

    def string_to_timedelta(self, s):
        pairs = [
            (float(amount), unit.lower())
            for amount, unit in self.duration_regex.findall(s)
        ]
        unit_aliases = {
            "days": {"d", "day", "days"},
            "hours": {"h", "hour", "hours", "hr", "hrs"},
            "minutes": {"m", "min", "mins", "minute", "minutes"},
            "seconds": {"s", "sec", "secs", "second", "seconds"},
        }
        kwargs = {}
        for amount, unit in pairs:
            if not amount:
                continue
            for unit_kw, aliases in unit_aliases.items():
                if unit in aliases:
                    kwargs[unit_kw] = amount
                    break
        return timedelta(**kwargs)


class AdminModelFormConverter(_BaseAdminModelConverter):
    @converts("sqlalchemy.sql.sqltypes.Interval")
    def convert_interval(self, field_args, **extra):
        return IntervalField(**field_args)

    @converts("Date")
    def convert_datetime(self, field_args, **extra):
        return DateField(**field_args)

    @converts("DateTime")
    def convert_datetime(self, field_args, **extra):
        return DateTimeField(**field_args)

    @converts("Text", "LargeBinary", "Binary", "CIText")  # includes UnicodeText
    def conv_Text(self, field_args, **extra):
        self._string_common(field_args=field_args, **extra)
        field_args.setdefault("render_kw", {}).setdefault("rows", 8)
        return fields.TextAreaField(**field_args)
