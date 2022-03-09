import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import dramatiq

from service.decorators import done_for
from service.dramatiqconfig import TASK_PARAMS
from settings import smtp_settings


@dramatiq.actor(
    max_retries=TASK_PARAMS.max_retries,
    queue_name=TASK_PARAMS.send_email_queue
)
@done_for
def send_email(receiver: str, subject: str, html_message: str) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
            smtp_settings.host, smtp_settings.port, context=context
    ) as server:
        server.login(smtp_settings.user, smtp_settings.password)
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = smtp_settings.user
        message["To"] = receiver
        body = MIMEText(html_message, "html")
        message.attach(body)
        server.sendmail(
            smtp_settings.user, receiver, message.as_string()
        )
