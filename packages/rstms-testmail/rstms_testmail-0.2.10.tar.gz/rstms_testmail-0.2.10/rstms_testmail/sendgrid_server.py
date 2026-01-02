import sendgrid
import sendgrid.helpers.mail


class SendGrid:

    def __init__(self, api_key):
        self.client = sendgrid.SendGridAPIClient(api_key=api_key)

    def send(self, from_addr, to_addr, subject, message_text):
        message = sendgrid.helpers.mail.Mail(
            from_email=from_addr,
            to_emails=to_addr,
            subject=subject,
            plain_text_content=message_text,
        )
        response = self.client.send(message)
        headers = response.headers
        self.result = {k: headers[k] for k in headers.keys()}
        return None
