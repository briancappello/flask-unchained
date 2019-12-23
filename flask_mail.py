# -*- coding: utf-8 -*-
"""
flaskext.mail
~~~~~~~~~~~~~

Flask extension for sending email.

Copyright (c) 2010 by danjac.

Some rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above
  copyright notice, this list of conditions and the following
  disclaimer in the documentation and/or other materials provided
  with the distribution.

* The names of the contributors may not be used to endorse or
  promote products derived from this software without specific
  prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import blinker
import re
import smtplib
import time
import unicodedata

from contextlib import contextmanager
from email import charset
from email.encoders import encode_base64
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.policy import SMTP
from email.utils import formataddr, formatdate, make_msgid, parseaddr

from flask import current_app


__version__ = '0.9.3'

charset.add_charset('utf-8', charset.SHORTEST, None, 'utf-8')


class FlaskMailUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self, obj, *args):
        self.obj = obj
        UnicodeDecodeError.__init__(self, *args)

    def __str__(self):
        original = UnicodeDecodeError.__str__(self)
        return '%s. You passed in %r (%s)' % (
            original, self.obj, type(self.obj)
        )


def force_text(s, encoding='utf-8', errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, str):
        return s

    try:
        if not isinstance(s, str):
            if isinstance(s, bytes):
                s = str(s, encoding, errors)
            else:
                s = str(s)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise FlaskMailUnicodeDecodeError(s, *e.args)
        else:
            s = ' '.join(force_text(arg, encoding, errors) for arg in s)
    return s


def sanitize_subject(subject, encoding='utf-8'):
    try:
        subject.encode('ascii')
    except UnicodeEncodeError:
        try:
            subject = Header(subject, encoding).encode()
        except UnicodeEncodeError:
            subject = Header(subject, 'utf-8').encode()
    return subject


def sanitize_address(addr, encoding='utf-8'):
    if isinstance(addr, str):
        addr = parseaddr(force_text(addr))
    nm, addr = addr

    try:
        nm = Header(nm, encoding).encode()
    except UnicodeEncodeError:
        nm = Header(nm, 'utf-8').encode()
    try:
        addr.encode('ascii')
    except UnicodeEncodeError:  # IDN
        if '@' in addr:
            localpart, domain = addr.split('@', 1)
            try:
                localpart = Header(localpart, encoding).encode()
            except UnicodeEncodeError:
                localpart = Header(localpart, 'utf-8').encode()
            domain = domain.encode('idna').decode('ascii')
            addr = '@'.join([localpart, domain])
        else:
            addr = Header(addr, encoding).encode()
    return formataddr((nm, addr))


def sanitize_addresses(addresses, encoding='utf-8'):
    return map(lambda e: sanitize_address(e, encoding), addresses)


def fix_recipients_list(recipients):
    fixed_recipients = []
    for recipient in recipients:
        if not isinstance(recipient, str):
            # Ensure that the name/email values are a tuple and not a list
            fixed_recipients.append(tuple(recipient))
        else:
            fixed_recipients.append(recipient)
    return fixed_recipients


def _has_newline(line):
    """Used by has_bad_header to check for \\r or \\n"""
    if line and ('\r' in line or '\n' in line):
        return True
    return False


class Connection:
    """Handles connection to host."""

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        if self.mail.suppress:
            self.host = None
        else:
            self.host = self.configure_host()

        self.num_emails = 0

        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.host and getattr(self.host, 'sock', None):
            try:
                self.host.quit()
            except smtplib.SMTPServerDisconnected:
                pass

    def configure_host(self):
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port)
        else:
            host = smtplib.SMTP(self.mail.server, self.mail.port)

        host.set_debuglevel(int(self.mail.debug))

        if self.mail.use_tls:
            (resp, reply) = host.starttls()
            # Fix CVE-2016-0772 on old Python installations
            if resp != 200:
                raise smtplib.SMTPResponseException(resp, reply)
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)

        return host

    def send(self, message, envelope_from=None):
        """Verifies and sends message.

        :param message: Message instance.
        :param envelope_from: Email address to be used in MAIL FROM command.
        """
        if not message.send_to:
            raise ValueError("No recipients have been added")

        if message.sender is None:
            raise ValueError("The message does not specify a sender and a default "
                             "sender has not been configured")

        if message.has_bad_headers():
            raise BadHeaderError

        if message.date is None:
            message.date = time.time()

        ret = None
        if self.host:
            ret = self.host.sendmail(
                sanitize_address(envelope_from or message.sender),
                list(sanitize_addresses(message.send_to)),
                message.as_bytes(),
                message.mail_options,
                message.rcpt_options
            )

        email_dispatched.send(message, app=current_app._get_current_object())

        self.num_emails += 1

        if self.num_emails == self.mail.max_emails:
            self.num_emails = 0
            if self.host:
                self.host.quit()
                self.host = self.configure_host()

        return ret

    def send_message(self, *args, **kwargs):
        """Shortcut for send(msg).

        Takes same arguments as Message constructor.

        :versionadded: 0.3.5
        """

        return self.send(Message(*args, **kwargs))


class BadHeaderError(Exception):
    pass


class Attachment:
    """Encapsulates file attachment information.

    :versionadded: 0.3.5

    :param filename: filename of attachment
    :param content_type: file mimetype
    :param data: the raw file data
    :param disposition: content-disposition (if any)
    :param content_id: content-id for inline reference
    """

    def __init__(self, filename=None, content_type=None, data=None,
                 disposition=None, headers=None, content_id=None):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition or 'attachment'
        self.headers = headers or {}
        self.content_id = content_id


class Message:
    """Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param alts: A dict or an iterable to go through dict() that contains
                 multipart alternatives
    :param sender: email sender address, or **MAIL_DEFAULT_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    :param reply_to: reply-to address
    :param date: send date
    :param charset: message character set
    :param extra_headers: A dictionary of additional headers for the message
    :param mail_options: A list of ESMTP options to be used in MAIL FROM
    :param rcpt_options:  A list of ESMTP options to be used in RCPT commands
    :param subtype:  Media subtype name for a message
    """

    def __init__(self, subject='',
                 recipients=None,
                 body=None,
                 html=None,
                 alts=None,
                 sender=None,
                 cc=None,
                 bcc=None,
                 attachments=None,
                 reply_to=None,
                 date=None,
                 charset=None,
                 extra_headers=None,
                 mail_options=None,
                 rcpt_options=None,
                 subtype=None):

        sender = sender or current_app.extensions['mail'].default_sender

        if isinstance(sender, tuple):
            sender = "%s <%s>" % sender

        self.recipients = recipients or []
        self.subject = subject
        self.sender = sender
        self.reply_to = reply_to
        self.cc = cc or []
        self.bcc = bcc or []
        self.body = body
        self.alts = dict(alts or {})
        self.html = html
        self.date = date
        self.msgId = make_msgid()
        self.charset = charset
        self.extra_headers = extra_headers
        self.subtype = subtype
        self.mail_options = mail_options or []
        self.rcpt_options = rcpt_options or []
        self.attachments = attachments or []

    @property
    def recipients(self):
        return self._recipients

    @recipients.setter
    def recipients(self, recipients):
        self._recipients = fix_recipients_list(recipients)

    @property
    def cc(self):
        return self._cc

    @cc.setter
    def cc(self, recipients):
        self._cc = fix_recipients_list(recipients)

    @property
    def bcc(self):
        return self._bcc

    @bcc.setter
    def bcc(self, recipients):
        self._bcc = fix_recipients_list(recipients)

    @property
    def send_to(self):
        return set(self.recipients) | set(self.bcc or ()) | set(self.cc or ())

    @property
    def html(self):
        return self.alts.get('html')

    @html.setter
    def html(self, value):
        if value is None:
            self.alts.pop('html', None)
        else:
            self.alts['html'] = value

    def _mimetext(self, text, subtype=None):
        """Creates a MIMEText object with the given subtype (default: 'plain')
        If the text is unicode, the utf-8 charset is used.
        """
        subtype = subtype or 'plain'
        charset = self.charset or 'utf-8'
        return MIMEText(text, _subtype=subtype, _charset=charset)

    def _message(self):
        """Creates the email"""
        ascii_attachments = current_app.extensions['mail'].ascii_attachments
        encoding = self.charset or 'utf-8'

        attachments = self.attachments or []

        if not attachments and not self.alts:
            # No html content and zero attachments means plain text
            msg = self._mimetext(self.body, self.subtype)
        elif attachments and not self.alts:
            # No html and at least one attachment means multipart
            subtype = self.subtype or 'mixed'
            msg = MIMEMultipart(_subtype=subtype)
            msg.attach(self._mimetext(self.body))
        else:
            # Anything else
            subtype = self.subtype or 'mixed'
            msg = MIMEMultipart(_subtype=subtype)
            alternative = MIMEMultipart(_subtype='alternative')
            alternative.attach(self._mimetext(self.body))
            for mimetype, content in self.alts.items():
                alternative.attach(self._mimetext(content, mimetype))
            msg.attach(alternative)

        if self.subject:
            msg['Subject'] = sanitize_subject(force_text(self.subject),
                                              encoding)

        msg['From'] = sanitize_address(self.sender, encoding)
        msg['To'] = ', '.join(
            list(set(sanitize_addresses(self.recipients, encoding)))
        )

        msg['Date'] = formatdate(self.date, localtime=True)
        # see RFC 5322 section 3.6.4.
        msg['Message-ID'] = self.msgId

        if self.cc:
            msg['Cc'] = ', '.join(
                list(set(sanitize_addresses(self.cc, encoding)))
            )

        if self.reply_to:
            msg['Reply-To'] = sanitize_address(self.reply_to, encoding)

        if self.extra_headers:
            for k, v in self.extra_headers.items():
                msg[k] = v

        SPACES = re.compile(r'[\s]+', re.UNICODE)
        for attachment in attachments:
            f = MIMEBase(*attachment.content_type.split('/'))
            f.set_payload(attachment.data)
            encode_base64(f)

            filename = attachment.filename
            if filename and ascii_attachments:
                # force filename to ascii
                filename = unicodedata.normalize('NFKD', filename)
                filename = filename.encode('ascii', 'ignore').decode('ascii')
                filename = SPACES.sub(u' ', filename).strip()

            try:
                filename and filename.encode('ascii')
            except UnicodeEncodeError:
                filename = ('UTF8', '', filename)

            f.add_header('Content-Disposition',
                         attachment.disposition,
                         filename=filename)

            for key, value in attachment.headers.items():
                f.add_header(key, value)

            if attachment.content_id:
                try:
                    f.replace_header('Content-ID', attachment.content_id)
                except KeyError:
                    f.add_header('Content-ID', attachment.content_id)

            msg.attach(f)
        msg.policy = SMTP
        return msg

    def as_string(self):
        return self._message().as_string()

    def as_bytes(self):
        return self._message().as_string().encode(self.charset or 'utf-8')

    def __str__(self):
        return self.as_string()

    def __bytes__(self):
        return self.as_bytes()

    def has_bad_headers(self):
        """
        Checks for bad headers i.e. newlines in subject, sender or recipients.
        RFC5322 allows multiline CRLF with trailing whitespace (FWS) in headers
        """
        headers = [self.sender, self.reply_to] + self.recipients
        for header in headers:
            if _has_newline(header):
                return True

        if self.subject:
            if _has_newline(self.subject):
                for linenum, line in enumerate(self.subject.split('\r\n')):
                    if not line:
                        return True
                    if linenum > 0 and line[0] not in '\t ':
                        return True
                    if _has_newline(line):
                        return True
                    if not line.strip():
                        return True
        return False

    def is_bad_headers(self):
        from warnings import warn
        warn(DeprecationWarning('is_bad_headers is deprecated, use the'
                                ' new has_bad_headers method instead.'),
             stacklevel=1)
        return self.has_bad_headers()

    def send(self, connection):
        """
        Verifies and sends the message.
        """
        return connection.send(self)

    def add_recipient(self, recipient):
        """
        Adds another recipient to the message.

        :param recipient: email address of recipient.
        """
        self.recipients.append(recipient)

    def attach(self,
               filename=None,
               content_type=None,
               data=None,
               disposition=None,
               headers=None,
               content_id=None):
        """
        Adds an attachment to the message.

        :param filename: filename of attachment
        :param content_type: file mimetype
        :param data: the raw file data
        :param disposition: content-disposition (if any)
        :param content_id: content-id
        """
        self.attachments.append(
            Attachment(filename, content_type, data, disposition,
                       headers, content_id)
        )


class _MailMixin:
    @contextmanager
    def record_messages(self):
        """
        Records all messages. Use in unit tests for example::

            with mail.record_messages() as outbox:
                response = app.test_client.get("/email-sending-view/")
                assert len(outbox) == 1
                assert outbox[0].subject == "testing"

        You must have blinker installed in order to use this feature.
        :versionadded: 0.4
        """

        if not email_dispatched:
            raise RuntimeError("blinker must be installed")

        outbox = []

        def _record(message, app):  # skipcq: PYL-W0613 (unused arg)
            outbox.append(message)

        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)

    def send(self, message):
        """
        Sends a single message instance. If TESTING is True the message will
        not actually be sent.

        :param message: a Message instance.
        """

        with self.connect() as connection:
            return message.send(connection)

    def send_message(self, *args, **kwargs):
        """
        Shortcut for send(msg).

        Takes same arguments as Message constructor.

        :versionadded: 0.3.5
        """

        return self.send(Message(*args, **kwargs))

    def connect(self):
        """
        Opens a connection to the mail host.
        """
        app = getattr(self, "app", None) or current_app
        try:
            return Connection(app.extensions['mail'])
        except KeyError:
            raise RuntimeError("The curent application was"
                               " not configured with Flask-Mail")


class _Mail(_MailMixin):
    def __init__(self, server, username, password, port, use_tls, use_ssl,
                 default_sender, debug, max_emails, suppress,
                 ascii_attachments=False):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.default_sender = default_sender
        self.debug = debug
        self.max_emails = max_emails
        self.suppress = suppress
        self.ascii_attachments = ascii_attachments


class Mail(_MailMixin):
    """
    Manages email messaging

    :param app: Flask instance
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.state = self.init_app(app)
        else:
            self.state = None

    def init_mail(self, config, debug=False, testing=False):
        return _Mail(
            config.get('MAIL_SERVER', '127.0.0.1'),
            config.get('MAIL_USERNAME'),
            config.get('MAIL_PASSWORD'),
            config.get('MAIL_PORT', 25),
            config.get('MAIL_USE_TLS', False),
            config.get('MAIL_USE_SSL', False),
            config.get('MAIL_DEFAULT_SENDER'),
            int(config.get('MAIL_DEBUG', debug)),
            config.get('MAIL_MAX_EMAILS'),
            config.get('MAIL_SUPPRESS_SEND', testing),
            config.get('MAIL_ASCII_ATTACHMENTS', False)
        )

    def init_app(self, app):
        """Initializes your mail settings from the application settings.

        You can use this if you want to set up your Mail instance
        at configuration time.

        :param app: Flask application instance
        """
        state = self.init_mail(app.config, app.debug, app.testing)

        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mail'] = state
        return state

    def __getattr__(self, name):
        return getattr(self.state, name, None)


signals = blinker.Namespace()

email_dispatched = signals.signal("email-dispatched", doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
""")
