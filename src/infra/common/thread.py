import threading
from typing import Any, Callable, Mapping


class StoppableThread(threading.Thread):
    """Convenience class for creating stoppable threads."""

    def __init__(
            self,
            target: Callable[[], None] | None = None,
            kwargs: Mapping[str, Any] | None = None,
            stopped_event: threading.Event | None = None,
    ):
        super().__init__(target=target, kwargs=kwargs)
        self.__stopped_event = stopped_event or threading.Event()

    @property
    def stopped_event(self) -> threading.Event:
        return self.__stopped_event

    def should_keep_running(self) -> bool:
        """Determines whether the thread should continue running."""
        return not self.__stopped_event.is_set()

    def on_thread_stop(self) -> None:
        """Override this method instead of :meth:`stop()`.
        :meth:`stop()` calls this method.

        This method is called immediately after the thread is signaled to stop.
        """
        pass

    def stop(self) -> None:
        """Signals the thread to stop."""
        self.__stopped_event.set()
        self.on_thread_stop()

    def on_thread_start(self) -> None:
        """Override this method instead of :meth:`start()`. :meth:`start()`
        calls this method.

        This method is called right before this thread is started and this
        object’s run() method is invoked.
        """
        pass

    def start(self) -> None:
        self.on_thread_start()
        super().start()
