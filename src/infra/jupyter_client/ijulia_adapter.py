from jupyter_client import AsyncKernelClient, KernelClient

from src.application.ijulia_adapter.interfaces import IJuliaAdapter


class JCIJuliaAdapter(IJuliaAdapter):
    def __init__(self, client: KernelClient) -> None:
        self.jupyter_client = client

    def execute_code(self, code: str, source_id: str) -> str:
        return self.jupyter_client.execute(code, user_expressions={"source": source_id})

    def send_stdin(self, input_data: str) -> None:
        self.jupyter_client.input(input_data)
        return None
