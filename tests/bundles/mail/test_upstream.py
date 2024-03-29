# -*- coding: utf-8 -*-
"""
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

from __future__ import with_statement

import base64
import email
import re
import smtplib
import socket
import threading
import time
import unittest

from contextlib import contextmanager
from email.header import Header
from unittest import mock

from flask import Flask
from speaklater import make_lazy_string

from flask_mail import BadHeaderError, Connection, Mail, Message, sanitize_address


class TestCase(unittest.TestCase):
    TESTING = True
    MAIL_DEFAULT_SENDER = "support@mysite.com"

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(self)
        self.assertTrue(self.app.testing)
        self.mail = Mail(self.app)
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    @contextmanager
    def mail_config(self, **settings):
        """
        Context manager to alter mail config during a test and restore it
        after, even in case of a failure.
        """
        original = {}
        state = self.mail.state
        for key in settings:
            assert hasattr(state, key)
            original[key] = getattr(state, key)
            setattr(state, key, settings[key])

        yield
        # restore
        for k, v in original.items():
            setattr(state, k, v)

    def assertIn(self, member, container, msg=None):
        if hasattr(unittest.TestCase, "assertIn"):
            return unittest.TestCase.assertIn(self, member, container, msg)
        return self.assertTrue(member in container)

    def assertNotIn(self, member, container, msg=None):
        if hasattr(unittest.TestCase, "assertNotIn"):
            return unittest.TestCase.assertNotIn(self, member, container, msg)
        return self.assertFalse(member in container)

    def assertIsNone(self, obj, msg=None):
        if hasattr(unittest.TestCase, "assertIsNone"):
            return unittest.TestCase.assertIsNone(self, obj, msg)
        return self.assertTrue(obj is None)

    def assertIsNotNone(self, obj, msg=None):
        if hasattr(unittest.TestCase, "assertIsNotNone"):
            return unittest.TestCase.assertIsNotNone(self, obj, msg)
        return self.assertTrue(obj is not None)


class TestInitialization(TestCase):
    def test_init_mail(self):
        mail = self.mail.init_mail(self.app.config, self.app.debug, self.app.testing)

        self.assertEqual(self.mail.state.__dict__, mail.__dict__)


class TestMessage(TestCase):
    def test_initialize(self):
        msg = Message(subject="subject", recipients=["to@example.com"])
        self.assertEqual(msg.sender, self.app.extensions["mail"].default_sender)
        self.assertEqual(msg.recipients, ["to@example.com"])

    def test_recipients_properly_initialized(self):
        msg = Message(subject="subject")
        self.assertEqual(msg.recipients, [])
        msg2 = Message(subject="subject")
        msg2.add_recipient("somebody@here.com")
        self.assertEqual(len(msg2.recipients), 1)

    def test_fix_recipients_list(self):
        msg = Message(subject="test")
        msg.recipients = [["Test", "to@example.com"]]
        assert msg.recipients[0] == ("Test", "to@example.com")

    def test_esmtp_options_properly_initialized(self):
        msg = Message(subject="subject")
        self.assertEqual(msg.mail_options, [])
        self.assertEqual(msg.rcpt_options, [])

        msg = Message(subject="subject", mail_options=["BODY=8BITMIME"])
        self.assertEqual(msg.mail_options, ["BODY=8BITMIME"])

        msg2 = Message(subject="subject", rcpt_options=["NOTIFY=SUCCESS"])
        self.assertEqual(msg2.rcpt_options, ["NOTIFY=SUCCESS"])

    def test_sendto_properly_set(self):
        msg = Message(
            subject="subject",
            recipients=["somebody@here.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
        )
        self.assertEqual(len(msg.send_to), 3)
        msg.add_recipient("cc@example.com")
        self.assertEqual(len(msg.send_to), 3)

    def test_add_recipient(self):
        msg = Message("testing")
        msg.add_recipient("to@example.com")
        self.assertEqual(msg.recipients, ["to@example.com"])

    def test_sender_as_tuple(self):
        msg = Message(subject="testing", sender=("tester", "tester@example.com"))
        self.assertEqual("tester <tester@example.com>", msg.sender)

    def test_default_sender_as_tuple(self):
        self.app.extensions["mail"].default_sender = ("tester", "tester@example.com")
        msg = Message(subject="testing")
        self.assertEqual("tester <tester@example.com>", msg.sender)

    def test_reply_to(self):
        msg = Message(
            subject="testing",
            recipients=["to@example.com"],
            sender="spammer <spammer@example.com>",
            reply_to="somebody <somebody@example.com>",
            body="testing",
        )
        response = msg.as_string()

        addr = sanitize_address("somebody <somebody@example.com>")
        h = Header("Reply-To: %s" % addr)
        self.assertIn(h.encode(), str(response))

    def test_send_without_sender(self):
        self.app.extensions["mail"].default_sender = None
        msg = Message(subject="testing", recipients=["to@example.com"], body="testing")
        self.assertRaises(ValueError, self.mail.send, msg)

    def test_send_without_recipients(self):
        msg = Message(subject="testing", recipients=[], body="testing")
        self.assertRaises(ValueError, self.mail.send, msg)

    def test_bcc(self):
        msg = Message(
            sender="from@example.com",
            subject="testing",
            recipients=["to@example.com"],
            body="testing",
            bcc=["tosomeoneelse@example.com"],
        )
        response = msg.as_string()
        self.assertNotIn("tosomeoneelse@example.com", str(response))

    def test_cc(self):
        msg = Message(
            sender="from@example.com",
            subject="testing",
            recipients=["to@example.com"],
            body="testing",
            cc=["tosomeoneelse@example.com"],
        )
        response = msg.as_string()
        self.assertIn("Cc: tosomeoneelse@example.com", str(response))

    def test_attach(self):
        msg = Message(subject="testing", recipients=["to@example.com"], body="testing")
        msg.attach(data=b"this is a test", content_type="text/plain")
        a = msg.attachments[0]
        self.assertIsNone(a.filename)
        self.assertEqual(a.disposition, "attachment")
        self.assertEqual(a.content_type, "text/plain")
        self.assertEqual(a.data, b"this is a test")

    def test_bad_header_subject(self):
        msg = Message(
            subject="testing\r\n",
            sender="from@example.com",
            body="testing",
            recipients=["to@example.com"],
        )
        self.assertRaises(BadHeaderError, self.mail.send, msg)

    def test_multiline_subject(self):
        msg = Message(
            subject="testing\r\n testing\r\n testing \r\n \ttesting",
            sender="from@example.com",
            body="testing",
            recipients=["to@example.com"],
        )
        self.mail.send(msg)
        response = msg.as_string()
        self.assertIn("From: from@example.com", str(response))
        self.assertIn("testing\r\n testing\r\n testing \r\n \ttesting", str(response))

    def test_bad_multiline_subject(self):
        msg = Message(
            subject="testing\r\n testing\r\n ",
            sender="from@example.com",
            body="testing",
            recipients=["to@example.com"],
        )
        self.assertRaises(BadHeaderError, self.mail.send, msg)

        msg = Message(
            subject="testing\r\n testing\r\n\t",
            sender="from@example.com",
            body="testing",
            recipients=["to@example.com"],
        )
        self.assertRaises(BadHeaderError, self.mail.send, msg)

        msg = Message(
            subject="testing\r\n testing\r\n\n",
            sender="from@example.com",
            body="testing",
            recipients=["to@example.com"],
        )
        self.assertRaises(BadHeaderError, self.mail.send, msg)

    def test_bad_header_sender(self):
        msg = Message(
            subject="testing",
            sender="from@example.com\r\n",
            recipients=["to@example.com"],
            body="testing",
        )

        self.assertIn("From: from@example.com", msg.as_string())

    def test_bad_header_reply_to(self):
        msg = Message(
            subject="testing",
            sender="from@example.com",
            reply_to="evil@example.com\r",
            recipients=["to@example.com"],
            body="testing",
        )

        self.assertIn("From: from@example.com", msg.as_string())
        self.assertIn("To: to@example.com", msg.as_string())
        self.assertIn("Reply-To: evil@example.com", msg.as_string())

    def test_bad_header_recipient(self):
        msg = Message(
            subject="testing",
            sender="from@example.com",
            recipients=["to@example.com", "to\r\n@example.com"],
            body="testing",
        )

        self.assertIn("To: to@example.com", msg.as_string())

    def test_emails_are_sanitized(self):
        msg = Message(
            subject="testing",
            sender="sender\r\n@example.com",
            reply_to="reply_to\r\n@example.com",
            recipients=["recipient\r\n@example.com"],
        )
        self.assertIn("sender@example.com", msg.as_string())
        self.assertIn("reply_to@example.com", msg.as_string())
        self.assertIn("recipient@example.com", msg.as_string())

    def test_plain_message(self):
        plain_text = "Hello Joe,\nHow are you?"
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            body=plain_text,
        )
        self.assertEqual(plain_text, msg.body)
        self.assertIn("Content-Type: text/plain", msg.as_string())

    def test_message_str(self):
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            body="some plain text",
        )
        self.assertEqual(msg.as_string(), str(msg))

    def test_plain_message_with_attachments(self):
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            body="hello",
        )

        msg.attach(data=b"this is a test", content_type="text/plain")

        self.assertIn("Content-Type: multipart/mixed", msg.as_string())

    def test_plain_message_with_ascii_attachment(self):
        msg = Message(subject="subject", recipients=["to@example.com"], body="hello")

        msg.attach(
            data=b"this is a test", content_type="text/plain", filename="test doc.txt"
        )

        self.assertIn(
            "Content-Disposition: attachment;" ' filename="test doc.txt"',
            msg.as_string(),
        )

    def test_plain_message_with_unicode_attachment(self):
        msg = Message(subject="subject", recipients=["to@example.com"], body="hello")

        msg.attach(
            data=b"this is a test",
            content_type="text/plain",
            filename="ünicöde ←→ ✓.txt",
        )

        parsed = email.message_from_string(msg.as_string())

        disposition = parsed.get_payload()[1].get("Content-Disposition")
        self.assertIn(
            re.sub(r"\s+", " ", disposition),
            [
                "attachment; filename*=\"UTF8''%C3%BCnic%C3%B6de%20"
                '%E2%86%90%E2%86%92%20%E2%9C%93.txt"',
                "attachment; filename*=UTF8''%C3%BCnic%C3%B6de%20"
                "%E2%86%90%E2%86%92%20%E2%9C%93.txt",
            ],
        )

    def test_plain_message_with_ascii_converted_attachment(self):
        with self.mail_config(ascii_attachments=True):
            msg = Message(subject="subject", recipients=["to@example.com"], body="hello")

            msg.attach(
                data=b"this is a test",
                content_type="text/plain",
                filename="ünicödeß ←.→ ✓.txt",
            )

            parsed = email.message_from_string(msg.as_string())
            self.assertIn(
                'Content-Disposition: attachment; filename="unicode . .txt"',
                parsed.as_string(),
            )

    def test_html_message(self):
        html_text = "<p>Hello World</p>"
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            html=html_text,
        )

        self.assertEqual(html_text, msg.html)
        self.assertIn("Content-Type: multipart/alternative", msg.as_string())
        self.assertIn("Content-Type: text/html", msg.as_string())

    def test_json_message(self):
        json_text = '{"msg": "Hello World!}'
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            alts={"json": json_text},
        )

        self.assertEqual(json_text, msg.alts["json"])
        self.assertIn("Content-Type: multipart/alternative", msg.as_string())

    def test_html_message_with_attachments(self):
        html_text = "<p>Hello World</p>"
        plain_text = "Hello World"
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            body=plain_text,
            html=html_text,
        )
        msg.attach(data=b"this is a test", content_type="text/plain")

        self.assertEqual(html_text, msg.html)
        self.assertIn("Content-Type: multipart/alternative", msg.as_string())
        self.assertIn("Content-Type: text/html", msg.as_string())
        self.assertIn("Content-Type: text/plain", msg.as_string())

        parsed = email.message_from_string(msg.as_string())
        self.assertEqual(len(parsed.get_payload()), 2)

        body, attachment = parsed.get_payload()
        self.assertEqual(len(body.get_payload()), 2)

        plain, html = body.get_payload()
        self.assertEqual(plain.get_payload(), plain_text)
        self.assertEqual(html.get_payload(), html_text)
        self.assertEqual(base64.b64decode(attachment.get_payload()), b"this is a test")

    def test_date_header(self):
        before = time.time()
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            body="hello",
            date=time.time(),
        )
        after = time.time()

        self.assertTrue(before <= msg.date <= after)
        dateFormatted = email.utils.formatdate(msg.date, localtime=True)
        self.assertIn("Date: " + dateFormatted, msg.as_string())

    def test_msgid_header(self):
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            body="hello",
        )

        # see RFC 5322 section 3.6.4. for the exact format specification
        r = re.compile(r"<\S+@\S+>").match(msg.msgId)
        self.assertIsNotNone(r)
        self.assertIn("Message-ID: " + msg.msgId, msg.as_string())

    def test_unicode_sender_tuple(self):
        msg = Message(
            subject="subject",
            sender=("ÄÜÖ → ✓", "from@example.com>"),
            recipients=["to@example.com"],
        )

        self.assertIn(
            "From: =?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <from@example.com>",
            msg.as_string(),
        )

    def test_unicode_sender(self):
        msg = Message(
            subject="subject",
            sender="ÄÜÖ → ✓ <from@example.com>>",
            recipients=["to@example.com"],
        )

        self.assertIn(
            "From: =?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <from@example.com>",
            msg.as_string(),
        )

    def test_unicode_headers(self):
        msg = Message(
            subject="subject",
            sender="ÄÜÖ → ✓ <from@example.com>",
            recipients=["Ä <t1@example.com>", "Ü <t2@example.com>"],
            cc=["Ö <cc@example.com>"],
        )

        response = msg.as_string()
        a1 = sanitize_address("Ä <t1@example.com>")
        a2 = sanitize_address("Ü <t2@example.com>")
        h1_a = Header("To: %s, %s" % (a1, a2))
        h1_b = Header("To: %s, %s" % (a2, a1))
        a3 = sanitize_address("ÄÜÖ → ✓ <from@example.com>")
        h2 = Header("From: %s" % a3)
        h3 = Header("Cc: %s" % sanitize_address("Ö <cc@example.com>"))

        # Ugly, but there's no guaranteed order of the recipients in the header
        try:
            self.assertIn(h1_a.encode(), response)
        except AssertionError:
            self.assertIn(h1_b.encode(), response)

        self.assertIn(h2.encode(), response)
        self.assertIn(h3.encode(), response)

    def test_unicode_subject(self):
        msg = Message(
            subject=make_lazy_string(lambda a: a, "sübject"),
            sender="from@example.com",
            recipients=["to@example.com"],
        )
        self.assertIn(b"=?utf-8?q?s=C3=BCbject?=", msg.as_bytes())

        subject = "[Foo Bar] Voici vos paramètres d'accès à"
        msg = Message(
            subject=make_lazy_string(lambda a: a, subject),
            sender="from@example.com",
            recipients=["to@example.com"],
        )
        self.assertIn(
            b"=?utf-8?b?W0ZvbyBCYXJdIFZvaWNpIHZvcyBwYX"
            b"JhbcOodHJlcyBkJ2FjY8OocyDDoA==?=",
            msg.as_bytes(),
        )

    def test_extra_headers(self):
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            body="hello",
            extra_headers={"X-Extra-Header": "Yes"},
        )
        self.assertIn("X-Extra-Header: Yes", msg.as_string())

    def test_message_charset(self):
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["foo@bar.com"],
            charset="us-ascii",
        )

        # ascii body
        msg.body = "normal ascii text"
        self.assertIn('Content-Type: text/plain; charset="us-ascii"', msg.as_string())

        # ascii html
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["foo@bar.com"],
            charset="us-ascii",
        )
        msg.body = None
        msg.html = "<html><h1>hello</h1></html>"
        self.assertIn('Content-Type: text/html; charset="us-ascii"', msg.as_string())

        # unicode body
        msg = Message(
            sender="from@example.com", subject="subject", recipients=["foo@bar.com"]
        )
        msg.body = "ünicöde ←→ ✓"
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())

        # unicode body and unicode html
        msg = Message(
            sender="from@example.com", subject="subject", recipients=["foo@bar.com"]
        )
        msg.html = "ünicöde ←→ ✓"
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())
        self.assertIn('Content-Type: text/html; charset="utf-8"', msg.as_string())

        # unicode body and attachments
        msg = Message(
            sender="from@example.com", subject="subject", recipients=["foo@bar.com"]
        )
        msg.html = None
        msg.attach(data=b"foobar", content_type="text/csv")
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())

        # unicode sender as tuple
        msg = Message(
            sender=("送信者", "from@example.com"),
            subject="表題",
            recipients=["foo@bar.com"],
            reply_to="返信先 <somebody@example.com>",
            charset="shift_jis",
        )  # japanese
        msg.body = "内容"
        self.assertIn("From: =?iso-2022-jp?", msg.as_string())
        self.assertNotIn("From: =?utf-8?", msg.as_string())
        self.assertIn("Subject: =?iso-2022-jp?", msg.as_string())
        self.assertNotIn("Subject: =?utf-8?", msg.as_string())
        self.assertIn("Reply-To: =?iso-2022-jp?", msg.as_string())
        self.assertNotIn("Reply-To: =?utf-8?", msg.as_string())
        self.assertIn('Content-Type: text/plain; charset="iso-2022-jp"', msg.as_string())

        # unicode subject sjis
        msg = Message(
            sender="from@example.com",
            subject="表題",
            recipients=["foo@bar.com"],
            charset="shift_jis",
        )  # japanese
        msg.body = "内容"
        self.assertIn("Subject: =?iso-2022-jp?", msg.as_string())
        self.assertIn('Content-Type: text/plain; charset="iso-2022-jp"', msg.as_string())

        # unicode subject utf-8
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["foo@bar.com"],
            charset="utf-8",
        )
        msg.body = "内容"
        self.assertIn("Subject: subject", msg.as_string())
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())

        # ascii subject
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["foo@bar.com"],
            charset="us-ascii",
        )
        msg.body = "normal ascii text"
        self.assertNotIn("Subject: =?us-ascii?", msg.as_string())
        self.assertIn('Content-Type: text/plain; charset="us-ascii"', msg.as_string())

        # default charset
        msg = Message(
            sender="from@example.com", subject="subject", recipients=["foo@bar.com"]
        )
        msg.body = "normal ascii text"
        self.assertNotIn("Subject: =?", msg.as_string())
        self.assertIn('Content-Type: text/plain; charset="utf-8"', msg.as_string())

    def test_empty_subject_header(self):
        msg = Message(sender="from@example.com", recipients=["foo@bar.com"])
        msg.body = "normal ascii text"
        self.mail.send(msg)
        self.assertNotIn("Subject:", msg.as_string())

    def test_custom_subtype_without_attachment(self):
        msg = Message(
            sender="from@example.com",
            subject="testing",
            recipients=["to@example.com"],
            subtype="html",
        )
        self.assertIn("Content-Type: text/html", msg.as_string())

    def test_custom_subtype_with_attachment(self):
        msg = Message(
            sender="from@example.com",
            subject="testing",
            recipients=["to@example.com"],
            subtype="related",
        )
        msg.attach(data=b"this is a test", content_type="text/plain")
        self.assertIn("Content-Type: multipart/related", msg.as_string())


class TestMail(TestCase):
    def test_send(self):
        with self.mail.record_messages() as outbox:
            msg = Message(
                subject="testing", recipients=["tester@example.com"], body="test"
            )
            self.mail.send(msg)
            self.assertIsNotNone(msg.date)
            self.assertEqual(len(outbox), 1)
            sent_msg = outbox[0]
            default_sender = self.app.extensions["mail"].default_sender
            self.assertEqual(sent_msg.sender, default_sender)

    def test_send_message(self):
        with self.mail.record_messages() as outbox:
            self.mail.send_message(
                subject="testing", recipients=["tester@example.com"], body="test"
            )
            self.assertEqual(len(outbox), 1)
            msg = outbox[0]
            self.assertEqual(msg.subject, "testing")
            self.assertEqual(msg.recipients, ["tester@example.com"])
            self.assertEqual(msg.body, "test")
            default_sender = self.app.extensions["mail"].default_sender
            self.assertEqual(msg.sender, default_sender)


class TestConnection(TestCase):
    def test_send_message(self):
        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                conn.send_message(
                    subject="testing", recipients=["to@example.com"], body="testing"
                )
            self.assertEqual(len(outbox), 1)
            sent_msg = outbox[0]
            default_sender = self.app.extensions["mail"].default_sender
            self.assertEqual(sent_msg.sender, default_sender)

    def test_send_single(self):
        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                msg = Message(
                    subject="testing", recipients=["to@example.com"], body="testing"
                )
                conn.send(msg)
            self.assertEqual(len(outbox), 1)
            sent_msg = outbox[0]
            self.assertEqual(sent_msg.subject, "testing")
            self.assertEqual(sent_msg.recipients, ["to@example.com"])
            self.assertEqual(sent_msg.body, "testing")
            default_sender = self.app.extensions["mail"].default_sender
            self.assertEqual(sent_msg.sender, default_sender)

    def test_send_many(self):
        with self.mail.record_messages() as outbox:
            with self.mail.connect() as conn:
                for i in range(100):
                    msg = Message(
                        subject="testing", recipients=["to@example.com"], body="testing"
                    )
                    conn.send(msg)
            self.assertEqual(len(outbox), 100)
            sent_msg = outbox[0]
            default_sender = self.app.extensions["mail"].default_sender
            self.assertEqual(sent_msg.sender, default_sender)

    def test_send_without_sender(self):
        self.app.extensions["mail"].default_sender = None
        msg = Message(subject="testing", recipients=["to@example.com"], body="testing")
        with self.mail.connect() as conn:
            self.assertRaises(ValueError, conn.send, msg)

    def test_send_without_recipients(self):
        msg = Message(subject="testing", recipients=[], body="testing")
        with self.mail.connect() as conn:
            self.assertRaises(ValueError, conn.send, msg)

    def test_bad_header_subject(self):
        msg = Message(
            subject="testing\n\r", body="testing", recipients=["to@example.com"]
        )
        with self.mail.connect() as conn:
            self.assertRaises(BadHeaderError, conn.send, msg)

    def test_sendmail_with_ascii_recipient(self):
        with self.mail.connect() as conn:
            with mock.patch.object(conn, "host") as host:
                msg = Message(
                    subject="testing",
                    sender="from@example.com",
                    recipients=["to@example.com"],
                    body="testing",
                )
                conn.send(msg)

                host.sendmail.assert_called_once_with(
                    "from@example.com",
                    ["to@example.com"],
                    msg.as_bytes(),
                    msg.mail_options,
                    msg.rcpt_options,
                )

    def test_sendmail_with_non_ascii_recipient(self):
        with self.mail.connect() as conn:
            with mock.patch.object(conn, "host") as host:
                msg = Message(
                    subject="testing",
                    sender="from@example.com",
                    recipients=["ÄÜÖ → ✓ <to@example.com>"],
                    body="testing",
                )
                conn.send(msg)

                host.sendmail.assert_called_once_with(
                    "from@example.com",
                    ["=?utf-8?b?w4TDnMOWIOKGkiDinJM=?= <to@example.com>"],
                    msg.as_bytes(),
                    msg.mail_options,
                    msg.rcpt_options,
                )

    def test_sendmail_with_ascii_body(self):
        with self.mail.connect() as conn:
            with mock.patch.object(conn, "host") as host:
                msg = Message(
                    subject="testing",
                    sender="from@example.com",
                    recipients=["to@example.com"],
                    body="body",
                )
                conn.send(msg)

                host.sendmail.assert_called_once_with(
                    "from@example.com",
                    ["to@example.com"],
                    msg.as_bytes(),
                    msg.mail_options,
                    msg.rcpt_options,
                )

    def test_sendmail_with_non_ascii_body(self):
        with self.mail.connect() as conn:
            with mock.patch.object(conn, "host") as host:
                msg = Message(
                    subject="testing",
                    sender="from@example.com",
                    recipients=["to@example.com"],
                    body="Öö",
                )

                conn.send(msg)

                host.sendmail.assert_called_once_with(
                    "from@example.com",
                    ["to@example.com"],
                    msg.as_bytes(),
                    msg.mail_options,
                    msg.rcpt_options,
                )

    def test_configure_host_tls_failure(self):
        with mock.patch("flask_mail.smtplib.SMTP") as MockSMTP:
            mock_host = MockSMTP.return_value
            mock_host.starttls.return_value = (501, "Syntax error (testing)")
            with mock.patch.object(self.mail, "use_tls", True):
                self.assertTrue(self.mail.use_tls)
                self.assertRaises(
                    smtplib.SMTPResponseException, Connection(self.mail).configure_host
                )


class TestAgainstLocalServer(TestCase):
    def setUp(self):
        def bind_server_socket():
            server_socket = socket.socket()
            server_socket.bind(("localhost", 0))
            server_socket.settimeout(5)  # ensure thread dies
            server_socket.listen(1)
            return server_socket

        def server_threadfunc(server_socket, errors):
            try:
                client_socket, client_info = server_socket.accept()
                client_socket.settimeout(5)  # ensure thread dies
                client_socket.send(b"220 localhost ESMTP blah blah blah\r\n")
                client_socket.recv(1024)
                client_socket.send(b"250 ok\r\n")
                client_socket.close()  # unexpected disconnect
            except Exception as exc:
                errors.append(exc)

        server_socket = bind_server_socket()
        self.MAIL_SERVER, self.MAIL_PORT = server_socket.getsockname()
        self._server_errors = []
        thread = threading.Thread(
            target=server_threadfunc, args=(server_socket, self._server_errors)
        )
        self._server_thread = thread
        thread.daemon = True
        thread.start()
        super(TestAgainstLocalServer, self).setUp()
        self._old_app_mail_instance = self.app.extensions["mail"]
        self.app.extensions["mail"] = self.mail
        self.mail.suppress = False  # do live testing

    def tearDown(self):
        self._server_thread.join()
        assert not self._server_errors, self._server_errors
        self.app.extensions["mail"] = self._old_app_mail_instance
        super(TestAgainstLocalServer, self).tearDown()

    def test_detect_disconnect_during_send(self):
        msg = Message(
            sender="from@example.com",
            subject="subject",
            recipients=["to@example.com"],
            body="some plain text",
        )
        try:
            self.mail.send(msg)
            assert False  # exception expected
        except smtplib.SMTPServerDisconnected as e:
            assert "Connection unexpectedly closed" in e.args[0], e.args[0]


if __name__ == "__main__":
    unittest.main()
