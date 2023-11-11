import queue

import zmq
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

from config import StreamHandlerConfig
from src.application.executor_service.service import ExecutorService
from src.application.stream_adapter.dto import StreamMessage
from src.application.stream_adapter.interfaces import StreamAdapter
from src.infra.inmemory.stream_adapter import InmemoryStreamAdapter


def executor_service_scope(request: Request) -> ExecutorService:
    return request.app.state.executor_service()


def stream_adapter_scope(websocket: WebSocket) -> StreamAdapter:
    q: queue.Queue[StreamMessage] = websocket.app.state.queue()
    with q.mutex:
        q.queue.clear()

    return InmemoryStreamAdapter(mq=q)


def jinja2_scope(request: Request) -> Jinja2Templates:
    return request.app.state.jinja()