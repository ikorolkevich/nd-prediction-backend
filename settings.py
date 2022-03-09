import os
from pathlib import Path
from typing import NamedTuple

from jinja2 import Environment, PackageLoader, select_autoescape, \
    FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent


class JWTSettings(NamedTuple):
    secret_key: str
    lifetime: int


jwt_settings = JWTSettings(
    secret_key=os.environ.get('JWT_SECRET_KEY', 'SECRET'),
    lifetime=int(os.environ.get('JWT_LIFETIME', 60*24))
)


class PSQLDatabaseSettings(NamedTuple):
    user: str
    password: str
    host: str
    port: int
    db: str


psql_database_settings = PSQLDatabaseSettings(
    user=os.environ.get('PSQL_DATABASE_USER', 'user'),
    password=os.environ.get('PSQL_DATABASE_PASSWORD', 'password'),
    host=os.environ.get('PSQL_DATABASE_HOST', '127.0.0.1'),
    port=int(os.environ.get('PSQL_DATABASE_PORT', 5432)),
    db=os.environ.get('PSQL_DATABASE_DB', 'db'),
)


class TaskConfig(NamedTuple):
    name: str
    queue: str


send_verify_email_task = TaskConfig(
    name=os.environ.get('SEND_VERIFY_EMAIL', 'send_verify_email_task'),
    queue=os.environ.get('SEND_VERIFY_EMAIL_QUEUE', 'SEND_VERIFY_EMAIL')
)

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
    },
}

APP_NAME = 'ND-Prediction'

env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / 'templates')),
    autoescape=select_autoescape()
)


class SMTPSettings(NamedTuple):
    host: str
    port: int
    user: str
    password: str


smtp_settings = SMTPSettings(
    os.environ.get('SMTP_HOST', 'smtp.yandex.ru'),
    int(os.environ.get('SMTP_PORT', '465')),
    os.environ.get('SMTP_USER', 'korolkevich.i@yandex.ru'),
    os.environ.get('SMTP_PASSWORD', 'bcjsauoxkzyzvuwa'),
)
