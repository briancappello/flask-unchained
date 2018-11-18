import base64
import hashlib
import hmac

from datetime import timedelta
from flask_unchained import BaseService, current_app, injectable
from itsdangerous import BadSignature, SignatureExpired


class SecurityUtilsService(BaseService):
    """
    The security utils service. Mainly contains lower-level encryption/token handling
    code.
    """

    security = injectable
    user_manager = injectable

    def get_hmac(self, password):
        """
        Returns a Base64 encoded HMAC+SHA512 of the password signed with
        the salt specified by ``SECURITY_PASSWORD_SALT``.

        :param password: The password to sign.
        """
        salt = current_app.config.SECURITY_PASSWORD_SALT

        if salt is None:
            raise RuntimeError(
                'The configuration value `SECURITY_PASSWORD_SALT` must '
                'not be None when the value of `SECURITY_PASSWORD_HASH` is '
                'set to "%s"' % self.security.password_hash)

        h = hmac.new(encode_string(salt), encode_string(password), hashlib.sha512)
        return base64.b64encode(h.digest())

    def get_auth_token(self, user):
        """
        Returns the user's authentication token.
        """
        data = [str(user.id),
                self.security.hashing_context.hash(encode_string(user._password))]
        return self.security.remember_token_serializer.dumps(data)

    def verify_password(self, user, password):
        """
        Returns ``True`` if the password is valid for the specified user.

        Additionally, the hashed password in the database is updated if the
        hashing algorithm happens to have changed.

        :param user: The user to verify against
        :param password: The plaintext password to verify
        """
        if self.use_double_hash(user.password):
            verified = self.security.pwd_context.verify(
                self.get_hmac(password), user.password)
        else:
            # Try with original password.
            verified = self.security.pwd_context.verify(password, user.password)

        if verified and self.security.pwd_context.needs_update(user.password):
            user.password = password
            self.user_manager.save(user)
        return verified

    def hash_password(self, password):
        """
        Hash the specified plaintext password.

        It uses the configured hashing options.

        :param password: The plaintext password to hash
        """
        if self.use_double_hash():
            password = self.get_hmac(password).decode('ascii')

        return self.security.pwd_context.hash(
            password,
            **current_app.config.SECURITY_PASSWORD_HASH_OPTIONS.get(
                current_app.config.SECURITY_PASSWORD_HASH, {}))

    def hash_data(self, data):
        """
        Hash data in the security token hashing context.
        """
        return self.security.hashing_context.hash(encode_string(data))

    def verify_hash(self, hashed_data, compare_data):
        """
        Verify a hash in the security token hashing context.
        """
        return self.security.hashing_context.verify(
            encode_string(compare_data), hashed_data)

    def use_double_hash(self, password_hash=None):
        """
        Return a bool indicating whether a password should be hashed twice.
        """
        single_hash = current_app.config.SECURITY_PASSWORD_SINGLE_HASH
        if single_hash and self.security.password_salt:
            raise RuntimeError('You may not specify a salt with '
                               'SECURITY_PASSWORD_SINGLE_HASH')

        if password_hash is None:
            is_plaintext = self.security.password_hash == 'plaintext'
        else:
            is_plaintext = \
                self.security.pwd_context.identify(password_hash) == 'plaintext'

        return not (is_plaintext or single_hash)

    def generate_confirmation_token(self, user):
        """
        Generates a unique confirmation token for the specified user.

        :param user: The user to work with
        """
        data = [str(user.id), self.hash_data(user.email)]
        return self.security.confirm_serializer.dumps(data)

    def confirm_email_token_status(self, token):
        """
        Returns the expired status, invalid status, and user of a confirmation
        token. For example::

            expired, invalid, user = confirm_email_token_status('...')

        :param token: The confirmation token
        """
        expired, invalid, user, token_data = self.get_token_status(
            token, 'confirm', 'SECURITY_CONFIRM_EMAIL_WITHIN', return_data=True)

        if not invalid and user:
            user_id, token_email_hash = token_data
            invalid = not self.verify_hash(token_email_hash, user.email)

        return expired, invalid, user

    def generate_reset_password_token(self, user):
        """
        Generates a unique reset password token for the specified user.

        :param user: The user to work with
        """
        password_hash = self.hash_data(user.password) if user.password else None
        data = [str(user.id), password_hash]
        return self.security.reset_serializer.dumps(data)

    def reset_password_token_status(self, token):
        """
        Returns the expired status, invalid status, and user of a password reset
        token. For example::

            expired, invalid, user, data = reset_password_token_status('...')

        :param token: The password reset token
        """
        expired, invalid, user, data = self.get_token_status(
            token, 'reset', 'SECURITY_RESET_PASSWORD_WITHIN', return_data=True)

        if (not invalid
                and user.password
                and not self.verify_hash(data[1], user.password)):
            invalid = True

        return expired, invalid, user

    def get_token_status(self, token, serializer, max_age=None, return_data=False):
        """
        Get the status of a token.

        :param token: The token to check
        :param serializer: The name of the serializer. Can be one of the
                           following: ``confirm``, ``login``, ``reset``
        :param max_age: The name of the max age config option. Can be one of
                        the following: ``SECURITY_CONFIRM_EMAIL_WITHIN`` or
                        ``SECURITY_RESET_PASSWORD_WITHIN``
        """
        serializer = getattr(self.security, serializer + '_serializer')

        td = self.get_within_delta(max_age)
        max_age = td.seconds + td.days * 24 * 3600
        user, data = None, None
        expired, invalid = False, False

        try:
            data = serializer.loads(token, max_age=max_age)
        except SignatureExpired:
            d, data = serializer.loads_unsafe(token)
            expired = True
        except (BadSignature, TypeError, ValueError):
            invalid = True

        if data:
            user = self.user_manager.get(data[0])

        expired = expired and (user is not None)

        if return_data:
            return expired, invalid, user, data
        else:
            return expired, invalid, user

    def get_within_delta(self, key):
        """
        Get a timedelta object from the application configuration following
        the internal convention of::

            <Amount of Units> <Type of Units>

        Examples of valid config values::

            5 days
            10 minutes

        :param key: The config value key
        """
        txt = current_app.config.get(key)
        values = txt.split()
        return timedelta(**{values[1]: int(values[0])})

    # FIXME-identity
    @staticmethod
    def get_identity_attributes():
        attrs = current_app.config.SECURITY_USER_IDENTITY_ATTRIBUTES
        try:
            attrs = [f.strip() for f in attrs.split(',')]
        except AttributeError:
            pass
        return attrs

    # FIXME-identity
    def user_loader(self, user_identifier):
        try:
            user_identifier = int(user_identifier)
        except (ValueError, TypeError):
            for attr in self.get_identity_attributes():
                user = self.user_manager.get_by(**{attr: user_identifier})
                if user:
                    return user
        else:
            return self.user_manager.get(user_identifier)


def encode_string(string):
    """Encodes a string to bytes, if it isn't already.

    :param string: The string to encode"""

    if isinstance(string, str):
        string = string.encode('utf-8')
    return string
