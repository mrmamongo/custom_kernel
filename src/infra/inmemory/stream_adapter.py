from src.application.stream_adapter.dto import StreamMessage
from src.application.stream_adapter.interfaces import StreamAdapter

from queue import Queue


class InmemoryStreamAdapter(StreamAdapter):
    async def init(self) -> None:
        pass

    def __init__(self, mq: Queue[StreamMessage]):
        self.messages = mq

    def recv(self) -> StreamMessage:
        print(self.messages)
        return self.messages.get()
