import datetime
from logging.config import dictConfig

import uvicorn
from fastapi import Depends, FastAPI
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from tortoise.query_utils import Q

from backend.auth.users import auth_backend, \
    current_active_user, fastapi_users
from backend.nd_prediction.models import ForestFirePredictions, \
    ForestFirePredictionsPydantic
from backend.nd_prediction.schemas import FFProbabilityResponse
from settings import loging_config, SETTINGS


dictConfig(loging_config)
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


@app.get(
    "/api/weather/current_situation", dependencies=[Depends(current_active_user)],
    response_model=ForestFirePredictionsPydantic,
    tags=['weather']
)
async def current_situation():
    today = datetime.date.today()
    today = datetime.date(today.year - 1, today.month, today.day)
    qs = ForestFirePredictions.get(date=today)
    return await ForestFirePredictionsPydantic.from_queryset_single(qs)


@app.get(
    "/api/weather/ff_probabilities_dynamic",
    dependencies=[Depends(current_active_user)],
    response_model=FFProbabilityResponse,
    tags=['weather']
)
async def ff_probabilities_dynamic():
    today = datetime.date.today()
    today = datetime.date(today.year - 1, today.month, today.day)
    days = [today - datetime.timedelta(days=i) for i in range(1, 3)]
    days.append(today)
    for i in range(1, 3):
        days.append(today + datetime.timedelta(days=i))
    qs = await ForestFirePredictions.filter(Q(date__in=days))
    return FFProbabilityResponse(dynamic_data=qs)


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
