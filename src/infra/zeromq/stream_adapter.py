import zmq

from src.application.stream_adapter.dto import StreamMessage
from src.application.stream_adapter.interfaces import StreamAdapter


class ZMQStreamAdapter(StreamAdapter):
    def __init__(self, sender_port: int, notifier_port: int, *, context: zmq.Context | None = None) -> None:
        self.context = context or zmq.Context.instance()
        self.socket: zmq.Socket = context.socket(zmq.SUB)
        self.socket.connect(f"tcp://127.0.0.1:{sender_port}")
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")
        self.notifier_port = notifier_port

    def init(self):
        print("ZMQAdapter is busy")
        notifier: zmq.Socket = self.context.socket(zmq.REP)
        notifier.bind(f"tcp://127.0.0.1:{self.notifier_port}")
        notifier.recv()
        notifier.send(b"")
        notifier.close()
        print("ZMQAdapter is ready")

    def __enter__(self):
        return self

    def recv(self) -> StreamMessage:
        return StreamMessage.model_validate_json(self.socket.recv())

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.close()
