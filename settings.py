import os
from typing import NamedTuple


class JWTSettings(NamedTuple):
    secret_key: str
    lifetime: int


jwt_settings = JWTSettings(
    secret_key=os.environ.get('JWT_SECRET_KEY', 'SECRET'),
    lifetime=int(os.environ.get('JWT_LIFETIME', 3600))
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
