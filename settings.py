import json
from pathlib import Path

from pydantic import BaseModel
from jinja2 import Environment, select_autoescape, FileSystemLoader


BASE_DIR = Path(__file__).resolve().parent


class JWTSettings(BaseModel):
    secret_key: str
    lifetime: int


class PSQLDatabaseSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int
    db: str


class SMTPSettings(BaseModel):
    host: str
    port: int
    user: str
    password: str


class BackendSettings(BaseModel):
    jwt: JWTSettings
    psql: PSQLDatabaseSettings
    app_name: str


class RabbitmqSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int
    vhost: str


class TasksSettings(BaseModel):
    max_retries: int
    send_email_queue: str


class ServiceSettings(BaseModel):
    tasks: TasksSettings
    smtp: SMTPSettings


class Settings(BaseModel):
    backend: BackendSettings
    service: ServiceSettings
    rabbit: RabbitmqSettings


loging_config = {
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

env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / 'templates')),
    autoescape=select_autoescape()
)


with open(BASE_DIR / 'dev.config.json', 'r') as config_file:
    SETTINGS = Settings(**json.load(config_file))
