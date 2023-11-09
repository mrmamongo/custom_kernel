import logging
from typing import Any

from config import StreamHandlerConfig
from src.presentation.kernel_listener.listener import Message, Handler
from src.presentation.kernel_listener.zmq_sender import ZMQSender

logger = logging.getLogger(__name__)


def shell_handler(message: Message) -> None:
    logger.info(message, extra={"channel": "shell"})


class IopubHandler(Handler):
    def __init__(self, config: StreamHandlerConfig):
        self.config = config

    def __call__(self, message: Message) -> None:
        match message.message['msg_type']:
            case "status":
                print(f"STATUS {message.message['content']}")
            case "execute_input":
                print(f"EXEC_INP {message.message['content']}")
            case "stream":
                with ZMQSender(sender_port=self.config.sender_port, notifier_port=self.config.notifier_port) as sender:
                    sender.send(message.message['content'])


def stdin_handler(message: Message) -> None:
    logger.info(message, extra={"channel": "stdin"})


def control_handler(message: Message) -> None:
    logger.info(message, extra={"channel": "control"})
