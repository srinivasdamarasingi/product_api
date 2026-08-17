from pathlib import Path

from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
)
from jinja2 import Environment, FileSystemLoader

from app.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

# Configure Jinja2
BASE_DIR = Path(__file__).resolve().parent.parent

template_env = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates" / "emails")
)


def render_template(template_name: str, **context):
    template = template_env.get_template(template_name)
    return template.render(**context)


async def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    **context,
):
    html = render_template(
        template_name,
        **context,
    )

    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        body=html,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    await fm.send_message(message)