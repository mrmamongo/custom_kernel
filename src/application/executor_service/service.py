import asyncio
import functools
import logging
import queue
from uuid import UUID

import anyio
from jupyter_client import KernelManager

from src.application.executor.commands import (BaseCommand, ExecuteCommand,
                                               StdinCommand)
from src.application.executor.service import Executor
from src.application.executor_service.dto import Task
from src.infra.common.thread import StoppableThread


class ExecutorService:
    def __init__(self, kernel_manager: KernelManager, executor: Executor):
        self.__kernel_manager = kernel_manager
        self.__logger = logging.getLogger("ExecutorService")
        self.__executor = executor
        self.__executor.register_dependency(ExecutorService, self)
        self.__command_queue: queue.PriorityQueue[BaseCommand] = queue.PriorityQueue()
        self.__queue_handler_thread: StoppableThread = StoppableThread(
            target=asyncio.run, kwargs={"main": self.__handle_queue()}
        )

    def start(self) -> None:
        self.__queue_handler_thread.start()
        self.__logger.info("ExecutorService handler thread started")

    def join(self) -> None:
        self.__queue_handler_thread.stop()
        self.__logger.info("ExecutorService stopped")

    def execute_code(self, task: Task) -> None:
        self.__logger.info(f"Executing code: {task.source_id}")
        for index, block in enumerate(task.code_blocks):
            block.index = index
            self.__enqueue(
                command=ExecuteCommand(source_id=task.source_id, block=block)
            )

    def interrupt(self) -> None:
        self.clear_queue()
        self.__kernel_manager.interrupt_kernel()

    def stdin(self, source_id: str, stdin_data: str) -> None:
        self.__enqueue(command=StdinCommand(source_id=source_id, data=stdin_data))

    def clear_queue(self) -> None:
        with self.__command_queue.mutex:
            self.__command_queue.queue.clear()

    def __enqueue(self, command: BaseCommand) -> None:
        self.__command_queue.put(command)

    async def __handle_queue(self):
        while True:
            await self.__executor.execute_command(self.__command_queue.get())
