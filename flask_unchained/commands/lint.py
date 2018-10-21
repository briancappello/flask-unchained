# This command is adapted to click from Flask-Script 0.4.0
import os

from flask_unchained.cli import click


@click.command()
@click.option('-f', '--fix-imports', default=False, is_flag=True,
              help='Fix imports using isort, before linting')
def lint(fix_imports):
    """
    Run flake8.
    """
    from glob import glob
    from subprocess import call

    # FIXME: should support passing these in an option
    skip = [
        'ansible',
        'db',
        'flask_sessions',
        'node_modules',
        'requirements',
    ]
    root_files = glob('*.py')
    root_dirs = [name for name in next(os.walk('.'))[1]
                 if not name.startswith('.')]
    files_and_dirs = [x for x in root_files + root_dirs if x not in skip]

    def execute_tool(desc, *args):
        command = list(args) + files_and_dirs
        click.echo(f"{desc}: {' '.join(command)}")
        ret = call(command)
        if ret != 0:
            exit(ret)

    if fix_imports:
        execute_tool('Fixing import order', 'isort', '-rc')
    execute_tool('Checking code style', 'flake8')
