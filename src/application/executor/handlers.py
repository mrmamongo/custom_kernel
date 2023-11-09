import logging

from src.application.executor.commands import ExecuteCommand
from src.application.ijulia_adapter.interfaces import IJuliaAdapter

logger = logging.getLogger(__name__)


async def execute_code(data: ExecuteCommand, adapter: IJuliaAdapter):
    logger.info(f"Sending data to execution... {data.source_id} {data.block.code}")
    msg = adapter.execute_code(data.block.code, data.source_id)
    logger.info(f"Sent: {msg}")
