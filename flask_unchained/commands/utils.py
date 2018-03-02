import click

from typing import *

IterableOfStrings = Union[List[str], Tuple[str, ...]]
IterableOfTuples = Union[List[tuple], Tuple[tuple, ...]]


def print_table(column_names: IterableOfStrings,
                rows: IterableOfTuples,
                column_alignments: Optional[IterableOfStrings] = None,
                ) -> None:
    header_template = ''
    row_template = ''
    table_width = 0
    type_formatters = {int: 'd', float: 'f', str: 's'}
    types = [type_formatters.get(type(x), 'r') for x in rows[0]]

    alignments = {int: '>', float: '>'}
    column_alignments = (column_alignments or
                         [alignments.get(type(x), '<') for x in rows[0]])

    def get_column_width(idx):
        header_length = len(column_names[idx])
        content_length = max(len(str(row[idx])) for row in rows)
        return (content_length if content_length > header_length
                else header_length)

    for i in range(0, len(column_names)):
        col_width = get_column_width(i)
        header_col_template = f'{{:{col_width}}}'
        col_template = f'{{:{column_alignments[i]}{col_width}{types[i]}}}'
        if i == 0:
            header_template += header_col_template
            row_template += col_template
            table_width += col_width
        else:
            header_template += '  ' + header_col_template
            row_template += '  ' + col_template
            table_width += 2 + col_width

    click.echo(header_template.format(*column_names))
    click.echo('-' * table_width)

    for row in rows:
        try:
            click.echo(row_template.format(*row))
        except TypeError as e:
            raise TypeError(f'{e}: {row!r}')
