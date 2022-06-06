from fastapi_users_db_tortoise import TortoiseUserDatabase

from backend.auth.models import UserDB, UserModel


async def get_user_db():
    yield TortoiseUserDatabase(UserDB, UserModel)
