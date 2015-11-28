import getpass
import imaplib
import keyring
import smtplib

from email import Encoders
from email import message_from_string
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from settings.secure_settings import *

import BeautifulSoup
import HTMLParser
import textwrap

import os


class Mailer(object):

    def __init__(self, user=None, passwd=None):
        self.gmail_user = user
        self.gmail_passwd = passwd

    def login(self, user, passwd=None, stay_logged_in=True):
        self.gmail_user = user

        if passwd is None:
            passwd = keyring.get_password('shh-mailer', self.gmail_user)
        if passwd is None:
            passwd = getpass.getpass('Password for %s: ' % self.gmail_user)

        self.gmail_passwd = passwd

        if stay_logged_in:
            keyring.set_password('shh-mailer', self.gmail_user, self.gmail_passwd)

    def logout(self):
        keyring.delete_password('shh-mailer', self.gmail_user)
        self.gmail_user = None
        self.passwd = None

    def mail(self, to, subject, text, attach=None):
        if self.gmail_user is None:
            self.login(DEFAULT_EMAIL)

        msg = MIMEMultipart()
        msg['From'] = self.gmail_user
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        if attach:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(attach, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
            msg.attach(part)
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(self.gmail_user, self.gmail_passwd)
        mailServer.sendmail(self.gmail_user, to, msg.as_string())
        mailServer.close()

    def check_mail(self):
        if self.gmail_user is None:
            self.login(DEFAULT_EMAIL)

        # TODO(Bieber): Try out 'with' semantics
        M = imaplib.IMAP4_SSL('imap.gmail.com')
        M.login(self.gmail_user, self.gmail_passwd)
        M.select(readonly=1)
        rv, data = M.search(None, '(UNSEEN)')
        email_ids = data[0].split(' ')

        messages = []
        for num in reversed(email_ids):
            typ, data = M.fetch(num, '(RFC822)')
            msg = message_from_string(data[0][1])
            messages.append(Message(msg))

        M.close()
        return messages

class Message(object):

    def __init__(self, message):
        self.message = message

    def subject(self):
        return self.message['Subject']

    def sender(self):
        return self.message['From']

    def date_str(self):
        return self.message['Date']

    def text(self):
        msg = self.message
        h = HTMLParser.HTMLParser()
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                message = str(part.get_payload())
                message = message.replace('=C2=A0', ' ')  # non-breaking space
                message = message.replace('=E2=80=99', "'")  # Apostrophe
                print 'plain: """{}"""'.format(message)

            elif content_type == 'text/html':
                body = BeautifulSoup.BeautifulSoup(part.get_payload())
                p = element_find("p", body)
                font = element_find("font", body)
                div = element_find("div", body)
                synth_msg = textwrap.wrap(synthesize_elements(p, font, div))
                message = h.unescape(' '.join(synth_msg))
                message = message.replace('=  ', ' ')  # non-breaking space
                print 'html: """{}"""'.format(message)


        # TODO(Bieber): Shorten URLs to just domain name
        return message

# Helper functions for parsing body of email
def element_find(element, body):
    try:
        element = body.findAll(element)[0].text
    except IndexError:
        element = None

    return element

def synthesize_elements(*arg):
    message = []
    for i in range(len(arg)):
        if arg[i]:
            message.append(arg[i] + '. ')
    if not message:
        message = 'Undefinable'
    else:
        message = ', '.join(message)
    return message
