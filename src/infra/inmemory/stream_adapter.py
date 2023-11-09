from src.application.stream_adapter.dto import StreamMessage
from src.application.stream_adapter.interfaces import StreamAdapter

from queue import Queue


class InmemoryStreamAdapter(StreamAdapter):
    def __init__(self, mq: Queue[StreamMessage]):
        self.messages = mq

    def recv(self) -> StreamMessage:
        return self.messages.get()
