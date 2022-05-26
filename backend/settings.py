import json
from logging.config import dictConfig
from pathlib import Path

from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent


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


class Settings(BaseModel):
    backend: BackendSettings


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


with open(BASE_DIR / 'dev.config.json', 'r') as config_file:
    SETTINGS = Settings(**json.load(config_file))

dictConfig(loging_config)
