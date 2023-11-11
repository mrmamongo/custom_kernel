from fastapi import FastAPI
from starlette.templating import Jinja2Templates

from config import APIConfig
from src.presentation.fastapi.execution import router


def setup_fastapi(config: APIConfig) -> FastAPI:
    app = FastAPI()

    jinja = Jinja2Templates(config.templates_dir)
    app.state.jinja = lambda: jinja

    app.include_router(router)

    return app
