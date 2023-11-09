from fastapi import FastAPI

from config import APIConfig
from src.presentation.fastapi.execution import router


def setup_fastapi(config: APIConfig) -> FastAPI:
    app = FastAPI()

    app.include_router(router)

    return app
