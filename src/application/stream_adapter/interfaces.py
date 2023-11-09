from abc import ABC, abstractmethod

from src.application.stream_adapter.dto import StreamMessage


class StreamAdapter(ABC):
    @abstractmethod
    async def init(self) -> None:
        pass
    @abstractmethod
    def recv(self) -> StreamMessage:
        pass
