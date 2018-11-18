from flask_unchained import FlaskForm, unchained
from sqlalchemy_unchained.validation import ValidationError, ValidationErrors


class ModelForm(FlaskForm):
    class Meta:
        model = None
        model_fields = {}

    def __init__(self, *args, **kwargs):
        try:
            model_name = self.Meta.model.__name__
            self.Meta.model = unchained.sqlalchemy_bundle.models[model_name]
        except KeyError:
            pass
        super().__init__(*args, **kwargs)

    def validate(self):
        validation_passed = super().validate()
        if not self.Meta.model:
            return validation_passed

        try:
            self.Meta.model.validate(**{k: v for k, v in self.data.items()
                                        if hasattr(self.Meta.model, k)})
        except ValidationErrors as e:
            for col_name, errors in e.errors.items():
                field = self._fields[col_name]
                for e in errors:
                    field.errors.append(e)

        if hasattr(self.Meta, 'model_fields'):
            for field_name, column_name in self.Meta.model_fields.items():
                field = self._fields[field_name]

                for v in self.Meta.model._get_validators(column_name):
                    try:
                        v(field.data)
                    except ValidationError as e:
                        e.model = self.Meta.model
                        e.column = column_name
                        field.errors.append(str(e))
                        validation_passed = False

        if not validation_passed:
            return validation_passed

        return len(self.errors) == 0

    @property
    def errors(self):
        if self._errors:
            return self._errors
        return dict((name, f.errors) for name, f in self._fields.items() if f.errors)

    @property
    def data(self):
        return dict((name, f.data) for name, f in self._fields.items())
