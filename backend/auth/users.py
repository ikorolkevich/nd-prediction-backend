import logging
import re
from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, \
    InvalidPasswordException
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import TortoiseUserDatabase

from backend.auth.db import get_user_db
from backend.auth.models import User, UserCreate, UserDB, UserUpdate
from settings import SETTINGS

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = SETTINGS.backend.jwt.secret_key
    verification_token_secret = SETTINGS.backend.jwt.secret_key
    password_regex = re.compile(
        r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$"
    )

    async def on_after_register(
            self, user: UserDB, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        logger.info(
            f"User {user.id} has forgot their password. Reset token: {token}"
        )

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        logger.info(
            f"Verification requested for user {user.id}. "
            f"Verification token: {token}"
        )

    async def validate_password(
            self,
            password: str,
            user: Union[UserCreate, UserDB],
    ) -> None:
        if re.search(self.password_regex, password) is None:
            raise InvalidPasswordException(
                reason="Пароль должен содержать от 8 до 15 символов, "
                       "содержать по крайней мере одну строчную букву, "
                       "одну прописную букву, одну цифру и "
                       "один специальный символ"
            )


async def get_user_manager(
        user_db: TortoiseUserDatabase = Depends(get_user_db)
):
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SETTINGS.backend.jwt.secret_key,
        lifetime_seconds=SETTINGS.backend.jwt.lifetime
    )


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_active_user = fastapi_users.current_user(active=True)
