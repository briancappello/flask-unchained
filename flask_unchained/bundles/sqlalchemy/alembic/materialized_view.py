from alembic.util import immutabledict  # NOQA (this *must* be first...  because alembic)
from alembic.autogenerate import comparators, renderers
from alembic.operations import Operations
from sqlalchemy.dialects.postgresql.base import PGInspector

from .reversible_op import ReversibleOp

# relevant docs
# http://alembic.zzzcomputing.com/en/latest/cookbook.html#replaceable-objects
# http://alembic.zzzcomputing.com/en/latest/api/autogenerate.html#autogen-custom-ops

class MaterializedViewMigration:
    def __init__(self, name, create_sql, drop_sql,
                 columns=None, indexes=None, prev=None):
        self.name = name
        self.create_sql = create_sql
        self.drop_sql = drop_sql
        self.indexes = indexes
        self.columns = columns
        self.prev = prev

    def __eq__(self, other):
        if not isinstance(other, MaterializedViewMigration):
            return False
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        # FIXME: this columns comparison is very coarse... at the least it
        # should probably also compare on types and/or nullable. however,
        # the challenge is that because the create sql for views is generated
        # from Selectable queries (instead of a Table/Model), the created views
        # can end up with slightly different representations from what the
        # metadata thinks. maybe it's a bug in the create_materialized_view
        # factory method?
        columns = tuple(c['name'] for c in self.columns)
        indexes = tuple(tuple((k, isinstance(v, list) and tuple(v) or v)
                              for k, v in index.items())
                        for index in self.indexes)
        return hash((self.name, columns, indexes))

    def __repr__(self):
        return '\n'.join(['MaterializedViewMigration(',
                          f'    {self.name!r},',
                          f'    """\n    {self.create_sql}\n    """,',
                          f'    {self.drop_sql!r},',
                          f'    indexes={self.indexes!r},',
                          ')'])


@Operations.register_operation("create_sql", "invoke_for_target")
@Operations.register_operation("replace_sql", "replace")
class CreateMaterializedViewOp(ReversibleOp):
    def reverse(self):
        return DropMaterializedViewOp(self.target)


@Operations.register_operation("drop_sql", "invoke_for_target")
class DropMaterializedViewOp(ReversibleOp):
    def reverse(self):
        return CreateMaterializedViewOp(self.target)


@renderers.dispatch_for(CreateMaterializedViewOp)
def render_create_sql(autogen_context, op):
    autogen_context.imports.add('import flask_unchained.bundles.sqlalchemy')
    template_args = autogen_context.migration_context.opts.get('template_args')
    template_args['migration_variables'].append(
        f'{op.target.name} = flask_unchained.bundles.sqlalchemy.{op.target}')

    if op.target.prev:
        return f'op.replace_sql({op.target.name}, replaces={op.target.prev!r})'
    return f'op.create_sql({op.target.name})'


@renderers.dispatch_for(DropMaterializedViewOp)
def render_drop_sql(autogen_context, op):
    if op.target.prev:
        return f'op.replace_sql({op.target.name}, ' \
               f'replace_with={op.target.prev!r})'
    return f'op.drop_sql({op.target.name})'


@Operations.implementation_for(CreateMaterializedViewOp)
def create_sql(operations, operation):
    operations.execute(operation.target.create_sql)
    for idx in operation.target.indexes:
        operations.create_index(operations.f(idx['name']),
                                operation.target.name,
                                idx['column_names'],
                                unique=idx['unique'])


@Operations.implementation_for(DropMaterializedViewOp)
def drop_sql(operations, operation):
    for idx in operation.target.indexes:
        operations.drop_index(operations.f(idx['name']),
                              table_name=operation.target.name)
    operations.execute(operation.target.drop_sql)


def create_replaceable_sql_for_existing(name, inspector, schema=None):
    query = inspector.get_view_definition(name, schema)
    columns = inspector.get_columns(name, schema)
    indexes = inspector.get_indexes(name, schema)
    return _create_replaceable_sql(name, query, columns, indexes)


def create_replaceable_sql_for_new(name, selectable, metadata):
    query = selectable.compile(compile_kwargs={'literal_binds': True})
    table = metadata.info['materialized_tables'][name]
    # columns and indexes should match the signature of return values from
    # inspect.get_columns and inspector.get_indexes
    columns = [{'name': c.name,
                'type': c.type,
                'nullable': c.nullable,
                'default': c.default,
                'autoincrement': c.autoincrement,
                'comment': c.comment}
               for c in table.columns]
    indexes = [{'name': idx.name,
                'unique': idx.unique,
                'column_names': [c.name for c in idx.columns]}
               for idx in table.indexes]
    return _create_replaceable_sql(name, query, columns, indexes)


def _create_replaceable_sql(name, query, columns, indexes):
    return MaterializedViewMigration(
        name,
        f'CREATE MATERIALIZED VIEW {name} AS {query}',
        f'DROP MATERIALIZED VIEW IF EXISTS {name}',
        columns,
        indexes,
    )


@comparators.dispatch_for('schema')
def compare_views(autogen_context, upgrade_ops, schemas):
    inspector = autogen_context.inspector
    if not isinstance(inspector, PGInspector):
        return  # this feature only works on postgres

    metadata = autogen_context.metadata
    prev_revision = autogen_context.migration_context.get_current_revision()

    # existing views (inspect their representation from the db)
    views = set()
    view_names = set()
    for schema in schemas:
        for name in inspector.get_view_names(include='materialized', schema=schema):
            views.add(create_replaceable_sql_for_existing(name, inspector, schema))
            view_names.add(name)

    # current metadata views (get their representation from current metadata)
    metadata_views = set()
    metadata_view_names = set()
    for name, selectable in metadata.info.setdefault('materialized_views', set()):
        metadata_views.add(create_replaceable_sql_for_new(name, selectable, metadata))
        metadata_view_names.add(name)

    creates = metadata_views.difference(views)
    drops = views.difference(metadata_views)
    upgrades = view_names.intersection(metadata_view_names)

    for replaceable_sql in creates:
        name = replaceable_sql.name
        if name in upgrades:
            replaceable_sql.prev = f'{prev_revision}.{name}'
        upgrade_ops.ops.append(CreateMaterializedViewOp(replaceable_sql))

    for replaceable_sql in drops:
        if replaceable_sql.name in upgrades:
            continue
        upgrade_ops.ops.append(DropMaterializedViewOp(replaceable_sql))
