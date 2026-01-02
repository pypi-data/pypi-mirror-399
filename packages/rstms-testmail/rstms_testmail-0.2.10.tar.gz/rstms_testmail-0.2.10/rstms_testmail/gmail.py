import base64
import tempfile
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .watcher import PortWatcher

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class Gmail:

    def __init__(self, credentials, reset_token=False):
        """credentials is a base64 encoded credentials.json file. (see https://console.cloud.google.com)"""

        self.credentials = credentials
        self.token_file = Path.home() / ".testmail" / ".testmail-gmail-token.json"
        if reset_token:
            self.token_file.unlink()

        with PortWatcher("ssh -q -N -R {}:localhost:{} beaker"):
            self.creds = self.authenticate_gmail_api()

            # create gmail api client
            self.service = build("gmail", "v1", credentials=self.creds)

    def authenticate_gmail_api(self):
        """Shows basic usage of the Gmail API."""

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if self.token_file.is_file():
            creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                with tempfile.NamedTemporaryFile() as tfp:
                    credentials = base64.b64decode(self.credentials.encode())
                    tfp.write(credentials)
                    tfp.flush()
                    tfp.seek(0)
                    flow = InstalledAppFlow.from_client_secrets_file(tfp.name, SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            self.token_file.write_text(creds.to_json())

        return creds

    def send(self, from_addr, to_addr, subject, message_text):
        """Create and send an email message."""
        service = self.service
        message = MIMEMultipart()
        message["to"] = to_addr
        message["from"] = from_addr
        message["subject"] = subject
        msg = MIMEText(message_text)
        message.attach(msg)

        # Encode the message in base64
        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        body = {"raw": raw}

        try:
            self.message = None
            self.message = service.users().messages().send(userId="me", body=body).execute()
            return None
        except Exception as error:
            return error

    def old_send(self, from_addr, to_addr, subject, message_text):
        """send a gmail message"""

        message = EmailMessage()

        message.set_content(message_text)

        message["To"] = to_addr
        message["From"] = from_addr
        message["Subject"] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message}}
        # pylint: disable=E1101
        send_message = self.service.users().messages().send(userId="me", body=create_message).execute()

        print(f'Message id: {send_message["id"]}')
        return send_message
