import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dramatiq

from service.decorators import done_for
from settings import SETTINGS


@dramatiq.actor(
    max_retries=SETTINGS.service.tasks.max_retries,
    queue_name=SETTINGS.service.tasks.send_email_queue
)
@done_for
def send_email(receiver: str, subject: str, html_message: str) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
            SETTINGS.service.smtp.host, SETTINGS.service.smtp.port,
            context=context
    ) as server:
        server.login(SETTINGS.service.smtp.user, SETTINGS.service.smtp.password)
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SETTINGS.service.smtp.user
        message["To"] = receiver
        body = MIMEText(html_message, "html")
        message.attach(body)
        server.sendmail(
            SETTINGS.service.smtp.user, receiver, message.as_string()
        )
