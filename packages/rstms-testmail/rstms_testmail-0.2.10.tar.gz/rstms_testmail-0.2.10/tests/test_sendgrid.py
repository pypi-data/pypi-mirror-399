import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def test_sendgrid_send():
    message = Mail(
        from_email=os.environ["TESTMAIL_FROM"],
        to_emails=os.environ["TESTMAIL_TO"],
        subject="Sending with Twilio SendGrid is Fun",
        plain_text_content="this is plain text email",
    )

    sendgrid_client = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
    response = sendgrid_client.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
