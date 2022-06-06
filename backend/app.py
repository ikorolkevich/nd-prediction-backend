import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware

from backend.auth.users import auth_backend, fastapi_users
from backend.nd_prediction.router import weather_router
from backend.settings import SETTINGS


app = FastAPI()
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.include_router(weather_router, prefix="/api/weather", tags=["weather"])


register_tortoise(
    app,
    db_url=f'postgres://'
           f'{SETTINGS.backend.psql.user}:{SETTINGS.backend.psql.password}@'
           f'{SETTINGS.backend.psql.host}:{SETTINGS.backend.psql.port}/'
           f'{SETTINGS.backend.psql.db}',
    modules={"models": ["backend.auth.models", "backend.nd_prediction.models"]},
    generate_schemas=True
)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
