import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

from src.application.executor_service.dto import CodeBlock, Languages, Task
from src.application.executor_service.service import ExecutorService
from src.application.stream_adapter.interfaces import StreamAdapter
from src.presentation.fastapi.dependencies import (executor_service_scope, stream_adapter_scope, jinja2_scope, )
from src.presentation.fastapi.text import html

router = APIRouter()


class ExecuteCodeModel(BaseModel):
    source_id: str = Field(alias="sourceId")
    code_cells: str = Field(alias="codeCells")

class StdinModel(BaseModel):
    source_id: str = Field(alias="sourceId")
    stdin_data: str = Field(alias="stdinData")

@router.post("/input")
async def send_stdin(stdin_model: StdinModel, executor_service: Annotated[ExecutorService, Depends(executor_service_scope)]):
    executor_service.stdin(stdin_model.source_id, stdin_model.stdin_data)


@router.post("/interrupt")
async def interrupt(executor_service: Annotated[ExecutorService, Depends(executor_service_scope)], ):
    await executor_service.interrupt()


@router.post("/execute")
def execute_code(data: ExecuteCodeModel,
                 executor_service: Annotated[ExecutorService, Depends(executor_service_scope)], ):
    task = Task(source_id=data.source_id,
                code_blocks=[CodeBlock(block_id="1", code=data.code_cells, language=Languages.PYTHON)], )
    executor_service.execute_code(task)


@router.get("/")
async def get_websocket(request: Request, jinja: Annotated[Jinja2Templates, Depends(jinja2_scope)]):
    return jinja.TemplateResponse('index.html', context={'request': request})


@router.websocket("/ws")
async def streaming_data(websocket: WebSocket,
                         stream_adapter: Annotated[StreamAdapter, Depends(stream_adapter_scope)], ):
    await websocket.accept()
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        while True:
            message = await loop.run_in_executor(func=stream_adapter.recv, executor=executor)
            await websocket.send_text(message.model_dump_json())
