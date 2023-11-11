from __future__ import annotations

import asyncio
import logging
import os
import queue

import aiohttp
import uvicorn
import zmq
from fastapi import FastAPI
from jupyter_client import AsyncKernelClient, AsyncKernelManager
from jupyter_client.session import Session

from config import Config, JupyterConfig, get_config
from src.application.executor_service.service import ExecutorService
from src.application.executor_service.setup import setup_executor_service
from src.application.stream_adapter.dto import StreamMessage
from src.presentation.fastapi.setup import setup_fastapi
from src.presentation.kernel_listener.handlers import (IopubHandler,
                                                       control_handler,
                                                       shell_handler,
                                                       stdin_handler)
from src.presentation.kernel_listener.listener import (KernelListener, Message,
                                                       SocketType)
from src.presentation.kernel_listener.setup import setup_kernel_listener

logger = logging.getLogger(__name__)


class App:
    def __init__(
        self,
        app: FastAPI,
        executor_service: ExecutorService,
        kernel_listener: KernelListener,
        config: Config,
        kernel_manager: AsyncKernelManager,
        kernel_client: AsyncKernelClient,
    ) -> None:
        self.app = app
        self.executor_service = executor_service
        self.kernel_listener = kernel_listener
        self.config = config
        self.kernel_manager = kernel_manager
        self.kernel_client = kernel_client

    @classmethod
    async def from_config(cls, config: Config) -> App:
        logging.basicConfig(level=logging.DEBUG)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:{config.api.server_port}/kernel_info"
            ) as resp:
                j = await resp.json()
                logger.info(j)
                config.jupyter = JupyterConfig.model_validate(j)

        logger.info(config.jupyter)
        app = setup_fastapi(config.api)
        app.state.stream_config = lambda: config.stream
        mq = queue.Queue[StreamMessage]()
        app.state.queue = lambda: mq

        kernel_session = Session(key=config.jupyter.key.encode(), username="mrmamongo")
        kernel_manager = AsyncKernelManager(
            session=kernel_session, **config.jupyter.model_dump()
        )
        kernel_client = AsyncKernelClient(
            session=kernel_session, **config.jupyter.model_dump()
        )
        kernel_client.start_channels(hb=False)
        await kernel_client.wait_for_ready()

        executor_service = setup_executor_service(kernel_client, kernel_manager)
        app.state.executor_service = lambda: executor_service

        kernel_listener = setup_kernel_listener(kernel_client.blocking_client())
        kernel_listener.state.queue = lambda: mq
        kernel_listener.state.config = lambda: config.stream

        kernel_listener.register_handler(SocketType.iopub_channel, IopubHandler)
        kernel_listener.register_handler(SocketType.stdin_channel, stdin_handler)
        kernel_listener.register_handler(SocketType.shell_channel, shell_handler)
        kernel_listener.register_handler(SocketType.control_channel, control_handler)

        logger.info(kernel_manager.get_connection_info())
        return cls(
            app=app,
            executor_service=executor_service,
            kernel_listener=kernel_listener,
            config=config,
            kernel_manager=kernel_manager,
            kernel_client=kernel_client,
            # zmq_context=zmq_context
        )

    async def start(self) -> None:
        self.executor_service.start()
        self.kernel_listener.start()
        server = uvicorn.Server(
            config=uvicorn.Config(
                app=self.app,
                host="0.0.0.0",
                port=int(self.config.api.client_port),
            )
        )
        await server.serve()

    async def dispose(self) -> None:
        self.kernel_client.stop_channels()
        self.zmq_context.destroy(1)


async def run():
    config = get_config()
    app = await App.from_config(config)
    try:
        await app.start()
    finally:
        await app.dispose()


def main() -> None:
    try:
        asyncio.run(run())
        exit(os.EX_OK)
    except SystemExit:
        exit(os.EX_OK)
    except Exception:
        logger.exception("Unexpected error occurred")
        exit(os.EX_SOFTWARE)


if __name__ == "__main__":
    main()
