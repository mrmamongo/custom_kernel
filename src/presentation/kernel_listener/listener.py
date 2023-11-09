import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, NamedTuple

import zmq
from jupyter_client import BlockingKernelClient
from jupyter_client.channels import ZMQSocketChannel
from starlette.datastructures import State

from src.infra.common.thread import StoppableThread


class SocketType(Enum):
    shell_channel = 0
    iopub_channel = 1
    stdin_channel = 2
    control_channel = 3


@dataclass
class SocketWrapper:
    socket: ZMQSocketChannel
    handlers: list


@dataclass
class Message:
    state: State
    message: dict[str, Any]


class Handler(ABC):
    @abstractmethod
    def __call__(self, msg: Message) -> None:
        pass


class StubHandler(Handler):
    def __init__(self, target: Callable[[Message], None]) -> None:
        self.target = target

    def __call__(self, msg: Message) -> None:
        self.target(msg)


class KernelListener(StoppableThread):
    def __init__(self, kernel_client: BlockingKernelClient) -> None:
        self.state = State()
        self.kernel_client = kernel_client
        self.sockets = {
            SocketType.shell_channel: SocketWrapper(
                socket=self.kernel_client.shell_channel, handlers=[]
            ),
            SocketType.iopub_channel: SocketWrapper(
                socket=self.kernel_client.iopub_channel, handlers=[]
            ),
            SocketType.stdin_channel: SocketWrapper(
                socket=self.kernel_client.stdin_channel, handlers=[]
            ),
            SocketType.control_channel: SocketWrapper(
                socket=self.kernel_client.control_channel, handlers=[]
            ),
        }
        self.poller = zmq.Poller()

        super().__init__()

    def register_handler(self, socket_type: SocketType, handler: Callable | Handler):
        """

        Два варианта:

        - class-based handler - фабрика хэндлеров, которая будет сама прокидывать все зависимости
        - DI Container + function-based handler - хэндлеры это функции, а зависимости прокидываются по сигнатуре

        TODO: выбрать один из вариантов и реализовать
        """
        if isinstance(handler, Handler):
            self.sockets[socket_type].handlers.append(handler)
            return
        if inspect.isclass(handler):
            def wrapper(message: Message) -> None:
                handler(message.state)(message)

            self.sockets[socket_type].handlers.append(StubHandler(target=wrapper))
        if inspect.isfunction(handler):
            self.sockets[socket_type].handlers.append(StubHandler(handler))
            return

    def on_thread_start(self):
        for key, sock in self.sockets.items():
            self.poller.register(sock.socket.socket)

    def run(self):
        while True:
            socks = dict(self.poller.poll())
            for wrapper in self.sockets.values():
                if socks.get(wrapper.socket.socket) == zmq.POLLIN:
                    message = wrapper.socket.get_msg()
                    for handler in wrapper.handlers:
                        handler(Message(state=self.state, message=message))

    def on_thread_stop(self):
        self.sockets.clear()
