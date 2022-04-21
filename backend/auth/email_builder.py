import abc
from typing import Tuple

from settings import env, SETTINGS


class BaseEmail:
    @abc.abstractmethod
    def get_subject(self) -> str:
        pass

    @abc.abstractmethod
    def get_context(self) -> dict:
        pass

    @abc.abstractmethod
    def get_template(self) -> str:
        pass


class ConfirmEmail(BaseEmail):

    def get_template(self) -> str:
        return 'conformation_email.html'

    def __init__(self, key: str):
        self.key = key

    def get_subject(self) -> str:
        return f'Email conformation. {SETTINGS.backend.app_name.upper()}'

    def get_context(self) -> dict:
        return {
            'activation_link': f'http://localhost:8000/{self.key}'
        }


class EmailBuilder:

    @classmethod
    def _build(cls, email_obj: BaseEmail) -> Tuple[str, str]:
        context = email_obj.get_context()
        subject = email_obj.get_subject()
        template = env.get_template(email_obj.get_template())
        return subject, template.render(**context)

    @classmethod
    def build_conformation_email(cls, key) -> Tuple[str, str]:
        email_cls = ConfirmEmail(key)
        return cls._build(email_cls)
