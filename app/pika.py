import json
from aio_pika import connect_robust
from functools import lru_cache

from app.main import logger
from . import config


@lru_cache()
def get_settings():
    """
    Config settings function.
    """
    return config.Settings()


conf_settings = get_settings()


class PikaAsyncClient():
    def __init__(self, process_callable):
        self.process_callable = process_callable

    async def consume(self, loop):
        """Setup message listener with the current running loop"""
        connection = await connect_robust(host=conf_settings.rabbit_host,
                                          port=conf_settings.rabbit_port,
                                          login=conf_settings.rabbit_user,
                                          password=conf_settings.rabbit_pass,
                                          virtualhost="/",
                                          loop=loop)
        channel = await connection.channel()
        queue = await channel.declare_queue(conf_settings.rabbit_consume_queue)
        await queue.consume(self.process_incoming_message, no_ack=False)
        logger.info('Established pika async listener')
        return connection

    async def process_incoming_message(self, message):
        """Processing incoming message from RabbitMQ"""
        await message.ack()
        body = message.body
        logger.debug('Received message')
        if body:
            self.process_callable(json.loads(body))
