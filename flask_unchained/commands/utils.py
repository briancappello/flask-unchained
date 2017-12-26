import click


def print_table(column_names, rows):
    header_template = ''
    row_template = ''
    table_width = 0
    type_formatters = {int: 'd', float: 'f', str: 's'}
    types = [type_formatters.get(type(x), 'r') for x in rows[0]]

    alignments = {int: '>', float: '>'}
    aligns = [alignments.get(type(x), '<') for x in rows[0]]

    def get_column_width(idx):
        header_length = len(column_names[idx])
        content_length = max(len(str(row[idx])) for row in rows)
        return content_length if content_length > header_length else header_length

    for i in range(0, len(column_names)):
        col_width = get_column_width(i)
        header_col_template = f'{{:{col_width}}}'
        col_template = f'{{:{aligns[i]}{col_width}{types[i]}}}'
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
        click.echo(row_template.format(*row))
