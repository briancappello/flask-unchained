# import our sqlalchemy types into generated migrations when needed
# http://alembic.zzzcomputing.com/en/latest/autogenerate.html#affecting-the-rendering-of-types-themselves
def render_migration_item(type_, obj, autogen_context):
    if obj is None:
        return False

    sqla_bundle = "flask_unchained.bundles.sqlalchemy.sqla.types"
    if sqla_bundle in obj.__module__:
        autogen_context.imports.add(f"import {sqla_bundle} as sqla_bundle")
        return f"sqla_bundle.{repr(obj)}"

    elif not (
        obj.__module__.startswith("sqlalchemy")
        or obj.__module__.startswith("flask_unchained")
    ):
        autogen_context.imports.add(f"import {obj.__module__}")
        return f"{obj.__module__}.{repr(obj)}"

    return False
