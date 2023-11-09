import logging
from typing import Any

from starlette.datastructures import State

from config import StreamHandlerConfig
from src.presentation.kernel_listener.listener import Message, Handler
from src.presentation.kernel_listener.zmq_sender import ZMQSender, InmemorySender

logger = logging.getLogger(__name__)


def shell_handler(message: Message) -> None:
    logger.info(message, extra={"channel": "shell"})


class IopubHandler(Handler):
    def __init__(self, state: State):
        self.state = state

    def __call__(self, message: Message) -> None:
        match message.message['msg_type']:
            case "status":
                print(f"STATUS {message.message['content']}")
            case "execute_input":
                print(f"EXEC_INP {message.message['content']}")
            case "stream":
                InmemorySender(self.state.queue).send(message.message['content'])


def stdin_handler(message: Message) -> None:
    logger.info(message, extra={"channel": "stdin"})


def control_handler(message: Message) -> None:
    logger.info(message, extra={"channel": "control"})
