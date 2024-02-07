def macro(name):
    """Replaces :func:`~flask_admin.model.template.macro`, adding support for using
    macros imported from another file. For example:

    .. code:: html+jinja

        {# templates/admin/column_formatters.html #}

        {% macro email(model, column) %}
          {% set address = model[column] %}
          <a href="mailto:{{ address }}">{{ address }}</a>
        {% endmacro %}

    .. code:: python

        class FooAdmin(ModelAdmin):
            column_formatters = {
                'col_name': macro('column_formatters.email')
            }

    Also required for this to work, is to add the following to the top of your
    master admin template:

    .. code:: html+jinja

        {# templates/admin/master.html #}

        {% import 'admin/column_formatters.html' as column_formatters with context %}
    """
    def wrapper(view, context, model, column):
        if '.' in name:
            macro_import_name, macro_name = name.split('.')
            m = getattr(context.get(macro_import_name), macro_name, None)
        else:
            m = context.resolve(name)

        if not m:
            return m

        return m(model=model, column=column)

    return wrapper
