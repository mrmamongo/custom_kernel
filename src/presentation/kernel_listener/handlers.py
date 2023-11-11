import logging

from starlette.datastructures import State

from src.presentation.kernel_listener.listener import Handler, Message
from src.presentation.kernel_listener.zmq_sender import InmemorySender

logger = logging.getLogger(__name__)


def shell_handler(message: Message) -> None:
    logger.info(message, extra={"channel": "shell"})


class IopubHandler(Handler):
    def __init__(self, state: State):
        self.state = state

    def __call__(self, message: Message) -> None:
        match message.message["msg_type"]:
            case "status":
                logger.info(f"STATUS {message.message['content']}")
            case "execute_input":
                logger.info(f"EXEC_INP {message.message['content']}")
            case "stream":
                logger.info(f"STREAM {message.message['content']}")
        InmemorySender(self.state.queue()).send(message.message["content"])


def stdin_handler(message: Message) -> None:
    InmemorySender(self.state.queue()).send(message.message["content"])


def control_handler(message: Message) -> None:
    logger.info(message, extra={"channel": "control"})
