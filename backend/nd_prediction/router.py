import datetime

from fastapi import APIRouter, Depends
from tortoise.query_utils import Q

from backend.auth.users import current_active_user
from backend.nd_prediction.models import ForestFirePredictionsPydantic, \
    ForestFirePredictions
from backend.nd_prediction.schemas import FFProbabilityResponse


weather_router = APIRouter()


@weather_router.get(
    "/current_situation",
    dependencies=[Depends(current_active_user)],
    response_model=ForestFirePredictionsPydantic,
    tags=['weather']
)
async def current_situation():
    today = datetime.date.today()
    # TODO remove after deploying
    today = datetime.date(today.year - 1, today.month, today.day)
    qs = ForestFirePredictions.get(date=today)
    return await ForestFirePredictionsPydantic.from_queryset_single(qs)


@weather_router.get(
    "/ff_probabilities_dynamic",
    dependencies=[Depends(current_active_user)],
    response_model=FFProbabilityResponse,
    tags=['weather']
)
async def ff_probabilities_dynamic():
    today = datetime.date.today()
    # TODO remove after deploying
    today = datetime.date(today.year - 1, today.month, today.day)
    days = [today - datetime.timedelta(days=i) for i in range(1, 3)]
    days.append(today)
    for i in range(1, 3):
        days.append(today + datetime.timedelta(days=i))
    qs = await ForestFirePredictions.filter(Q(date__in=days))
    return FFProbabilityResponse(dynamic_data=qs)
