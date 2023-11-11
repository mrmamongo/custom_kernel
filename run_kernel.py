import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from jupyter_client import AsyncKernelClient, AsyncKernelManager
from jupyter_client.session import Session
from starlette.requests import Request

from config import get_config

logger = logging.getLogger(__name__)


async def get_kernel_info(request: Request):
    return request.app.state.kernel_info()


async def main():
    app = FastAPI()
    config = get_config()

    app.get("/kernel_info")(get_kernel_info)
    # kernel_session = Session(key=config.jupyter.key.encode(), username="mrmamongo")
    kernel = AsyncKernelManager(**config.jupyter.model_dump(), cache_ports=False)
    await kernel.start_kernel()
    cl = kernel.client(**config.jupyter.model_dump())
    cl.start_channels()
    await cl.wait_for_ready()
    app.state.kernel_info = lambda: kernel.get_connection_info()
    logger.info(kernel.get_connection_info())
    server = uvicorn.Server(
        config=uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=int(config.api.server_port),
        )
    )

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
