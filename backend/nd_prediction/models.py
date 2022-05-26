from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model
from tortoise import fields


class ForestFirePredictions(Model):
    date = fields.DateField(unique=True)
    temp = fields.FloatField()
    dew_point = fields.FloatField()
    wind_speed = fields.FloatField()
    humidity = fields.FloatField()
    pressure = fields.FloatField()
    rainfall_24h = fields.FloatField()
    days_from_last_rain = fields.IntField()
    value = fields.FloatField()


ForestFirePredictionsPydantic = pydantic_model_creator(ForestFirePredictions)
