import asyncio
import logging
import threading

import uvicorn
import zmq
from fastapi import FastAPI
from jupyter_client import AsyncKernelClient, AsyncKernelManager
from jupyter_client.session import Session
from starlette.requests import Request

from config import get_config


IOPUB = "iopub"
STDIN = "stdin"
SHELL = "shell"
CONTROL = "control"


logger = logging.getLogger(__name__)


async def get_kernel_info(request: Request):
    return request.app.state.kernel_info()

async def listen_messages(kernel_manager: AsyncKernelManager):
    client = kernel_manager.client()
    client.start_channels()
    sources = {
        IOPUB: client.iopub_channel.socket,
        STDIN: client.stdin_channel.socket,
        SHELL: client.shell_channel.socket,
        CONTROL: client.control_channel.socket,
    }
    poller = zmq.Poller()
    for name, socket in sources.items():
        poller.register(socket, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())
        if socks.get(sources[STDIN]) == zmq.POLLIN:
            print('ALO')


async def main():
    app = FastAPI()
    config = get_config()

    app.get("/kernel_info")(get_kernel_info)
    # kernel_session = Session(key=config.jupyter.key.encode(), username="mrmamongo")
    kernel = AsyncKernelManager(**config.jupyter.model_dump(), cache_ports=False)
    await kernel.start_kernel()
    app.state.kernel_info = lambda: kernel.get_connection_info()
    logger.info(kernel.get_connection_info())
    threading.Thread(target=listen_messages, args=(kernel,), daemon=True)
    server = uvicorn.Server(
        config=uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=int(config.api.server_port),
        )
    )
    await server.serve()
    await kernel.shutdown_kernel()

if __name__ == "__main__":
    asyncio.run(main())
