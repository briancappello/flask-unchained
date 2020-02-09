import json

from flask_unchained import unchained
from flask_unchained.cli import cli, click


@cli.group()
def gql():
    """
    GraphQL commands.
    """


@gql.command('dump-schema')
@click.option("--out", "-o", default="schema.json", help="The filename to dump to.")
@click.option("--indent", default=4, help="How many spaces to indent the output by.")
def dump_schema(out, indent):
    root_schema = unchained.graphene_bundle.root_schema
    schema = dict(data=root_schema.introspect())
    with open(out, "w") as outfile:
        json.dump(schema, outfile, indent=indent, sort_keys=True)

    print(f"Successfully dumped GraphQL schema to {out}")
