try:
    from apispec.ext.marshmallow.openapi import (
        OpenAPIConverter as BaseOpenAPIConverter,
        LazyDict, OrderedLazyDict,
    )
except ImportError:
    from py_meta_utils import OptionalClass as BaseOpenAPIConverter
    from py_meta_utils import OptionalClass as LazyDict
    from py_meta_utils import OptionalClass as OrderedLazyDict

try:
    from marshmallow.compat import iteritems
    from marshmallow.utils import is_collection
except ImportError:
    from py_meta_utils import OptionalClass as iteritems
    from py_meta_utils import OptionalClass as is_collection


class OpenAPIConverter(BaseOpenAPIConverter):
    def fields2jsonschema(self, fields, schema=None, use_refs=True, dump=True, name=None):
        """Return the JSON Schema Object for a given marshmallow
        :class:`Schema <marshmallow.Schema>`. Schema may optionally provide the ``title`` and
        ``description`` class Meta options.

        https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#schemaObject

        Example: ::

            class UserSchema(Schema):
                _id = fields.Int()
                email = fields.Email(description='email address of the user')
                name = fields.Str()

                class Meta:
                    title = 'User'
                    description = 'A registered user'

            OpenAPI.schema2jsonschema(UserSchema)
            # {
            #     'title': 'User', 'description': 'A registered user',
            #     'properties': {
            #         'name': {'required': False,
            #                 'description': '',
            #                 'type': 'string'},
            #         '_id': {'format': 'int32',
            #                 'required': False,
            #                 'description': '',
            #                 'type': 'integer'},
            #         'email': {'format': 'email',
            #                 'required': False,
            #                 'description': 'email address of the user',
            #                 'type': 'string'}
            #     }
            # }

        :param Schema schema: A marshmallow Schema instance or a class object
        :rtype: dict, a JSON Schema Object
        """
        Meta = getattr(schema, 'Meta', None)
        if getattr(Meta, 'additional', None):
            declared_fields = set(schema._declared_fields.keys())
            if set(getattr(Meta, 'additional', set())) > declared_fields:
                import warnings
                warnings.warn(
                    'Only explicitly-declared fields will be included in the Schema Object. '
                    'Fields defined in Meta.fields or Meta.additional are ignored.',
                )

        jsonschema = {
            'type': 'object',
            'properties': (OrderedLazyDict() if getattr(Meta, 'ordered', None)
                           else LazyDict()),
        }

        exclude = set(getattr(Meta, 'exclude', []))

        for field_name, field_obj in iteritems(fields):
            if field_name in exclude or (field_obj.dump_only and not dump):
                continue

            observed_field_name = self._observed_name(field_obj, field_name)
            prop_func = lambda field_obj=field_obj: self.field2property(  # flake8: noqa
                field_obj, use_refs=use_refs, dump=dump, name=name,
            )
            jsonschema['properties'][observed_field_name] = prop_func

            partial = getattr(schema, 'partial', None)
            if field_obj.required:
                if not partial or (is_collection(partial) and field_name not in partial):
                    jsonschema.setdefault('required', []).append(observed_field_name)

        if 'required' in jsonschema:
            jsonschema['required'].sort()

        if Meta is not None:
            if hasattr(Meta, 'title'):
                jsonschema['title'] = Meta.title
            if hasattr(Meta, 'description'):
                jsonschema['description'] = Meta.description

        if getattr(schema, 'many', False):
            jsonschema = {
                'type': 'array',
                'items': jsonschema,
            }

        return jsonschema
