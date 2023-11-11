import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket

from src.application.executor_service.dto import CodeBlock, Languages, Task
from src.application.executor_service.service import ExecutorService
from src.application.stream_adapter.interfaces import StreamAdapter
from src.infra.zeromq.stream_adapter import ZMQStreamAdapter
from src.presentation.fastapi.dependencies import (executor_service_scope,
                                                   stream_adapter_scope)
from src.presentation.fastapi.text import html

router = APIRouter()


class ExecuteCodeModel(BaseModel):
    source_id: str = Field(alias="sourceId")
    code_cells: str = Field(alias="codeCells")


@router.post("/execute")
def execute_code(
    data: ExecuteCodeModel,
    executor_service: Annotated[ExecutorService, Depends(executor_service_scope)],
):
    task = Task(
        source_id=data.source_id,
        code_blocks=[
            CodeBlock(block_id="1", code=data.code_cells, language=Languages.PYTHON)
        ],
    )
    executor_service.execute_code(task)


@router.get("/websocket")
async def get_websocket():
    return HTMLResponse(html)


@router.websocket("/ws")
async def streaming_data(
    websocket: WebSocket,
    stream_adapter: Annotated[StreamAdapter, Depends(stream_adapter_scope)],
):
    await websocket.accept()
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as exec:
        while True:
            logging.error("Streaming data")
            message = await loop.run_in_executor(
                func=stream_adapter.recv, executor=exec
            )
            logging.error(stream_adapter)
            logging.error(message.model_dump_json())
            await websocket.send_text(message.model_dump_json())
