import pytest
import traceback

from flask_unchained.bundles.security.commands.roles import list_roles, create_role, delete_role


class TestRolesCommands:
    @pytest.mark.roles(dict(name='role1'),
                       dict(name='role2'),
                       dict(name='role3'))
    def test_list_roles(self, roles, cli_runner):
        result = cli_runner.invoke(list_roles)
        assert result.exit_code == 0, traceback.print_exception(*result.exc_info)

        lines = result.output.strip().splitlines()
        assert len(lines) == 5
        assert lines[0] == 'ID  Name '
        assert lines[1] == '---------'
        assert lines[-1] == f' {roles[-1].id}  {roles[-1].name}'
        assert lines[-2] == f' {roles[-2].id}  {roles[-2].name}'
        assert lines[-3] == f' {roles[-3].id}  {roles[-3].name}'

    def test_create_role(self, cli_runner):
        result = cli_runner.invoke(create_role, args=['--name', 'new-role'], input='y\n')
        assert result.exit_code == 0, traceback.print_exception(*result.exc_info)
        assert result.output.strip().splitlines()[-1] == \
            "Successfully created Role(id=1, name='new-role')"

    @pytest.mark.role(name='role1')
    def test_delete_role(self, role, cli_runner):
        result = cli_runner.invoke(delete_role, args=['name=role1'], input='y\n')
        assert result.exit_code == 0
        assert result.output.strip().splitlines()[-1] == \
            "Successfully deleted Role(id=1, name='role1')"
