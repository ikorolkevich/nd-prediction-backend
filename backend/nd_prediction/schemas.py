from typing import List

from pydantic import BaseModel

from backend.nd_prediction.models import ForestFirePredictionsPydantic


class FFProbabilityResponse(BaseModel):
    dynamic_data: List[ForestFirePredictionsPydantic]
