import asyncio

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI, Request
from functools import lru_cache
from loguru import logger

from app.helpers.order import receive_order
from app.pika import PikaAsyncClient
from app.routers import production
from . import config


@lru_cache()
def get_settings():
    """
    Config settings function.
    """
    return config.Settings()


conf_settings = get_settings()


class FoodProdApp(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pika_client = PikaAsyncClient(self.receive_incoming_order)

    @classmethod
    def receive_incoming_order(cls, message: dict):
        return receive_order(message)


# Create app
app = FoodProdApp(debug=conf_settings.debug)
app.add_middleware(CORSMiddleware)
app.include_router(production.router)

# Logger
logger.add("log_api.log", rotation="10 MB")  # Automatically rotate log file


@app.on_event('startup')
async def startup():
    loop = asyncio.get_running_loop()
    task = loop.create_task(app.pika_client.consume(loop))
    await task


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception(str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Database operation failed"},
    )


@app.get("/health")
def health():
    """
    Health router.
    """
    result = {
        "status": "ok"
    }
    return result
