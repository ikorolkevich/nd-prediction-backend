from logging.config import dictConfig

import uvicorn
from fastapi import Depends, FastAPI
from tortoise.contrib.fastapi import register_tortoise

from auth.models import UserDB
from auth.users import auth_backend, current_active_user, fastapi_users

from settings import psql_database_settings, log_config


dictConfig(log_config)

app = FastAPI()
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"]
)


@app.get("/authenticated-route")
async def authenticated_route(user: UserDB = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


register_tortoise(
    app,
    db_url=f'postgres://'
           f'{psql_database_settings.user}:{psql_database_settings.password}@'
           f'{psql_database_settings.host}:{psql_database_settings.port}/'
           f'{psql_database_settings.db}',
    modules={"models": ["auth.models"]},
    generate_schemas=True,
)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
