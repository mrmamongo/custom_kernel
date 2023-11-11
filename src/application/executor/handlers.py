import logging

from src.application.executor.commands import ExecuteCommand, StdinCommand
from src.application.ijulia_adapter.interfaces import IJuliaAdapter

logger = logging.getLogger(__name__)


async def stdin(data: StdinCommand, adapter: IJuliaAdapter):
    logger.info(f"Stdin command: {data.source_id} {data.data}")
    await adapter.send_stdin(data.data)


async def execute_code(data: ExecuteCommand, adapter: IJuliaAdapter):
    logger.info(f"Sending data to execution... {data.source_id} {data.block.code}")
    msg = await adapter.execute_code(data.block.code, data.source_id)
    logger.info(f"Sent: {msg}")
