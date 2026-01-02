import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid


class SMTPServer:

    def __init__(self, system, port, username, password, debug=None):
        self.protocol, _, self.server = system.partition(":")
        self.port = int(port)
        self.username = username
        self.password = password
        self.debug = debug

    def boundary(self):
        timestamp = str(int(time.time()))
        random_bytes = os.urandom(16).hex()
        return f"----boundary_{timestamp}_{random_bytes}"

    def send(self, from_addr, to_addr, subject, message):
        """
        Send an email using an SMTP server that requires SSL and authentication.

        Parameters:
        - from_addr: str - the sender's email address
        - to_addr: str - the recipient's email address
        - subject: str - the subject of the email
        - message: str - the body of the email
        """
        # Create the container email message.
        mime_message = MIMEMultipart(boundary=self.boundary())
        mime_message["Subject"] = subject
        mime_message["From"] = from_addr
        mime_message["To"] = to_addr
        mime_message["Message-ID"] = make_msgid()
        mime_message.attach(MIMEText(message, "plain"))

        # Connect to the SMTP server using SSL
        server = smtplib.SMTP_SSL(self.server, self.port)
        server.set_debuglevel(self.debug)
        server.login(self.username, self.password)
        payload = mime_message.as_bytes()
        ret = server.sendmail(from_addr, to_addr, payload)
        server.quit()
        self.result = ret
        return ret
