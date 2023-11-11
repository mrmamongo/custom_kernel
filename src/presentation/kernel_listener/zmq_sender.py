import queue

import zmq

from src.application.stream_adapter.dto import StreamMessage


class ZMQSender:
    def __init__(
        self,
        sender_port: int,
        notifier_port: int,
        *,
        context: zmq.Context | None = None,
    ):
        self.context = context or zmq.Context.instance()
        self.sender_socket: zmq.Socket = self.context.socket(zmq.PUB)
        self.sender_socket.bind(f"tcp://127.0.0.1:{sender_port}")
        self.notifier_port = notifier_port

    def __enter__(self):
        # print("ZMQSender is busy")
        # notifier_socket: zmq.Socket = self.context.socket(zmq.REQ)
        # notifier_socket.connect(f"tcp://127.0.0.1:{self.notifier_port}")
        #
        # notifier_socket.send(b"")
        # notifier_socket.recv()
        # notifier_socket.close()
        print("ZMQSender is ready")
        return self

    def send(self, message: dict) -> None:
        self.sender_socket.send_json(message)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sender_socket.close()


class InmemorySender:
    def __init__(self, mq: queue.Queue[StreamMessage]):
        self.mq = mq

    def send(self, message: dict) -> None:
        self.mq.put(StreamMessage(data=message))
