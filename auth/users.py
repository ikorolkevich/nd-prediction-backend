import logging
from typing import Optional

import celery
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import TortoiseUserDatabase

from auth.db import get_user_db
from auth.models import User, UserCreate, UserDB, UserUpdate
from settings import jwt_settings, send_verify_email_task


logger = logging.getLogger(__name__)


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = jwt_settings.secret_key
    verification_token_secret = jwt_settings.secret_key

    async def on_after_register(
            self, user: UserDB, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. "
                    f"Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        
        celery.signature(
            send_verify_email_task.name, args=(user.email, token)
        ).set(queue=send_verify_email_task.queue).apply_async()
        logger.info(f"Verification requested for user {user.id}. "
                    f"Verification token: {token}")


async def get_user_manager(
        user_db: TortoiseUserDatabase = Depends(get_user_db)
):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=jwt_settings.secret_key, lifetime_seconds=jwt_settings.lifetime
    )


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
