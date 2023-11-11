from fastapi import FastAPI
from jupyter_client import AsyncKernelClient, AsyncKernelManager

from src.application.executor.commands import ExecuteCommand
from src.application.executor.handlers import execute_code
from src.application.executor.service import Executor
from src.application.executor.state import ExecutorState
from src.application.executor_service.service import ExecutorService
from src.application.ijulia_adapter.interfaces import IJuliaAdapter
from src.infra.jupyter_client.ijulia_adapter import JCIJuliaAdapter


def setup_executor_service(
    kernel_client: AsyncKernelClient, kernel_manager: AsyncKernelManager
) -> ExecutorService:
    state = ExecutorState()
    executor = Executor(state)

    executor.register_dependency(IJuliaAdapter, lambda: JCIJuliaAdapter(kernel_client))

    executor.register_handler(ExecuteCommand, execute_code)
    executor_service = ExecutorService(kernel_manager, executor)

    return executor_service
