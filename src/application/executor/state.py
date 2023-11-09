from threading import Condition


class ExecutorState:
    def __init__(self) -> None:
        self._busy = Condition()

    def busy(self) -> None:
        self._busy.wait()

    def set_busy(self) -> None:
        self._busy.notify()
