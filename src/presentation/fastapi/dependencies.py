import queue

import zmq
from starlette.requests import Request
from starlette.websockets import WebSocket

from config import StreamHandlerConfig
from src.application.executor_service.service import ExecutorService
from src.application.stream_adapter.dto import StreamMessage
from src.application.stream_adapter.interfaces import StreamAdapter
from src.infra.inmemory.stream_adapter import InmemoryStreamAdapter
from src.infra.zeromq.stream_adapter import ZMQStreamAdapter
from src.presentation.kernel_listener.listener import Message


def executor_service_scope(request: Request) -> ExecutorService:
    return request.app.state.executor_service()


def stream_adapter_scope(websocket: WebSocket) -> StreamAdapter:
    q: queue.Queue[StreamMessage] = websocket.app.state.queue()
    with q.mutex:
        q.queue.clear()

    return InmemoryStreamAdapter(mq=q)


def zmq_stream_adapter_scope(websocket: WebSocket) -> StreamAdapter:
    config: StreamHandlerConfig = websocket.app.state.stream_config()
    context: zmq.Context = websocket.app.state.zmq_context()
    return ZMQStreamAdapter(config.sender_port, config.notifier_port, context=context)
