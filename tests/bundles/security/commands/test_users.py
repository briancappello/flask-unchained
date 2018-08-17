import pytest
import traceback

from flask_unchained.bundles.security.commands.users import (
    list_users, create_user, delete_user, set_password, confirm_user, activate_user,
    deactivate_user, add_role_to_user, remove_role_from_user)


@pytest.mark.security_bundle('flask_unchained.bundles.security')
class TestUsersCommands:
    @pytest.mark.users(dict(username='user1', email='user1@example.com'),
                       dict(username='user2', email='user2@example.com'),
                       dict(username='user3', email='user3@example.com'))
    def test_list_users(self, users, cli_runner):
        result = cli_runner.invoke(list_users)
        assert result.exit_code == 0, traceback.print_exception(*result.exc_info)

        lines = result.output.strip().splitlines()
        assert len(lines) == 5
        assert lines[0] == 'ID  Email              Active  Confirmed At         '
        assert lines[1] == '----------------------------------------------------'

        def user_line(user):
            return (f" {user.id}  "
                    f"{user.email}  "
                    f"{user.active}    "
                    f"{user.confirmed_at.strftime('%Y-%m-%d %H:%M%z')}")

        assert lines[-1] == user_line(users[-1])
        assert lines[-2] == user_line(users[-2])
        assert lines[-3] == user_line(users[-3])

    def test_create_user(self, cli_runner, user_manager):
        result = cli_runner.invoke(create_user, args=[
            '--email', 'a@a.com',
            '--password', 'password',
            '--active',
            '--confirmed-at', 'now',
        ], input='y\n')
        assert result.exit_code == 0
        assert result.output.strip().splitlines()[-1] == \
            "Successfully created User(id=1, email='a@a.com', active=True)"
        assert user_manager.get_by(email='a@a.com')

    def test_delete_user(self, user, cli_runner, user_manager):
        result = cli_runner.invoke(delete_user, args=['email=user@example.com'],
                                   input='y\n')
        assert result.exit_code == 0
        assert result.output.strip().splitlines()[-1] == \
            "Successfully deleted User(id=1, email='user@example.com', active=True)"
        assert not user_manager.get_by(email='user@example.com')

    @pytest.mark.user(password='old-password')
    def test_set_password(self, user, cli_runner, security_utils_service):
        assert security_utils_service.verify_and_update_password('old-password', user)
        result = cli_runner.invoke(set_password, args=[
            'email=user@example.com',
            '--password', 'new-password',
            '--no-email',
        ], input='y\n')
        assert result.exit_code == 0
        assert result.output.strip().splitlines()[-1] == \
            "Successfully updated password for " \
            "User(id=1, email='user@example.com', active=True)"
        assert security_utils_service.verify_and_update_password('new-password', user)

    @pytest.mark.user(confirmed_at=None)
    def test_confirm_user(self, user, cli_runner, user_manager):
        assert not user.confirmed_at
        result = cli_runner.invoke(confirm_user, args=['email=user@example.com'],
                                   input='y\n')
        user = user_manager.get_by(email='user@example.com')
        assert result.exit_code == 0
        assert user.confirmed_at
        assert result.output.strip().splitlines()[-1] == \
            "Successfully confirmed User(id=1, email='user@example.com', active=True) " \
            f"at {user.confirmed_at.strftime('%Y-%m-%d %H:%M:%S%z')}"

    @pytest.mark.user(active=False)
    def test_activate_user(self, user, cli_runner, user_manager):
        assert not user.active
        result = cli_runner.invoke(activate_user, args=['email=user@example.com'],
                                   input='y\n')
        user = user_manager.get_by(email='user@example.com')
        assert result.exit_code == 0
        assert result.output.strip().splitlines()[-1] == \
            "Successfully activated User(id=1, email='user@example.com', active=True)"
        assert user.active is True

    @pytest.mark.user(active=True)
    def test_deactivate_user(self, user, cli_runner, user_manager):
        assert user.active
        result = cli_runner.invoke(deactivate_user, args=['email=user@example.com'],
                                   input='y\n')
        user = user_manager.get_by(email='user@example.com')
        assert result.exit_code == 0
        assert result.output.strip().splitlines()[-1] == \
            "Successfully deactivated User(id=1, email='user@example.com', active=False)"
        assert user.active is False

    @pytest.mark.user(user_role=None, _user_role=None)
    @pytest.mark.role(name='new-role')
    def test_add_role(self, user, role, cli_runner, user_manager):
        assert not user.roles
        result = cli_runner.invoke(add_role_to_user, args=[
            '--user', 'email=user@example.com',
            '--role', 'name=new-role',
        ], input='y\n')
        user = user_manager.get_by(email='user@example.com')
        assert result.exit_code == 0
        assert result.output.strip().splitlines()[-1] == \
            "Successfully added Role(id=1, name='new-role') " \
            "to User(id=1, email='user@example.com', active=True)"
        assert role in user.roles

    @pytest.mark.user(user_role=None)
    def test_remove_role(self, user, cli_runner, user_manager):
        assert len(user.roles) == 1
        role = user.roles[0]
        result = cli_runner.invoke(remove_role_from_user, args=[
            '--user', 'email=user@example.com',
            '--role', f'name={role.name}',
        ], input='y\n')
        user = user_manager.get_by(email='user@example.com')
        assert result.exit_code == 0
        assert result.output.strip().splitlines()[-1] == \
            f"Successfully removed Role(id=1, name='{role.name}') " \
            f"from User(id=1, email='user@example.com', active=True)"
        assert not user.roles
