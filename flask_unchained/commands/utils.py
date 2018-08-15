from flask_unchained import click
import subprocess

from typing import *

IterableOfStrings = Union[List[str], Tuple[str, ...]]
IterableOfTuples = Union[List[tuple], Tuple[tuple, ...]]


def print_table(column_names: IterableOfStrings,
                rows: IterableOfTuples,
                column_alignments: Optional[IterableOfStrings] = None,
                primary_column_idx: int = 0,
                ) -> None:
    """
    Prints a table of information to the console. Automatically determines if the
    console is wide enough, and if not, displays the information in list form.

    :param column_names: The heading labels
    :param rows: A list of lists
    :param column_alignments: An optional list of strings, using either '<' or '>'
        to specify left or right alignment respectively
    :param primary_column_idx: Used when displaying information in list form,
        to determine which label should be the top-most one. Defaults to the first
        label in ``column_names``.
    """
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

    # check if we can format the table horizontally
    if table_width < get_terminal_width():
        click.echo(header_template.format(*column_names))
        click.echo('-' * table_width)

        for row in rows:
            try:
                click.echo(row_template.format(*row))
            except TypeError as e:
                raise TypeError(f'{e}: {row!r}')

    # otherwise format it vertically
    else:
        max_label_width = max(*[len(label) for label in column_names])
        non_primary_columns = [(i, col) for i, col in enumerate(column_names)
                               if i != primary_column_idx]
        for row in rows:
            type_ = types[primary_column_idx]
            row_template = f'{{:>{max_label_width}s}}: {{:{type_}}}'
            click.echo(row_template.format(column_names[primary_column_idx],
                                           row[primary_column_idx]))
            for i, label in non_primary_columns:
                row_template = f'{{:>{max_label_width}s}}: {{:{types[i]}}}'
                click.echo(row_template.format(label, row[i]))
            click.echo()


def get_terminal_width():
    try:
        r = subprocess.run(['tput', 'cols'],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    except:
        pass
    else:
        if r.returncode == 0:
            return int(r.stdout.decode('ascii').strip())
    return 80
