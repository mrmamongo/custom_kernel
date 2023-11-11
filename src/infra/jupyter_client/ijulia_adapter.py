from jupyter_client import AsyncKernelClient

from src.application.ijulia_adapter.interfaces import IJuliaAdapter


class JCIJuliaAdapter(IJuliaAdapter):
    def __init__(self, client: AsyncKernelClient) -> None:
        self.jupyter_client = client

    async def execute_code(self, code: str, source_id: str) -> str:
        return self.jupyter_client.execute(
            code, allow_stdin=True
        )

    async def send_stdin(self, input_data: str) -> None:
        self.jupyter_client.input(input_data)
        return None
