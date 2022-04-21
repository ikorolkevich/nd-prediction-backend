import pika
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dramatiq.middleware import CurrentMessage, Prometheus

from settings import SETTINGS


rabbitmq_broker = RabbitmqBroker(
    host=SETTINGS.rabbit.host, port=SETTINGS.rabbit.port,
    virtual_host=SETTINGS.rabbit.vhost,
    credentials=pika.PlainCredentials(
        username=SETTINGS.rabbit.user,
        password=SETTINGS.rabbit.password
    )
)
rabbitmq_broker.middleware = list(
    filter(lambda x: not isinstance(x, Prometheus), rabbitmq_broker.middleware)
)
rabbitmq_broker.add_middleware(CurrentMessage())
dramatiq.set_broker(rabbitmq_broker)
