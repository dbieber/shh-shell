import getpass
import imaplib
import smtplib

from email import Encoders
from email import message_from_string
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import os

class Mailer(object):

    def __init__(self, user="you@should.login", passwd="wrong password"):
        self.gmail_user = user
        self.gmail_passwd = passwd

    def login(self, user, passwd=None):
        self.gmail_user = user
        self.gmail_passwd = passwd or getpass.getpass('Password for %s: ' % self.gmail_user)


    def mail(self, to, subject, text, attach=None):
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
            messages.append(msg)

        M.close()
        return messages
