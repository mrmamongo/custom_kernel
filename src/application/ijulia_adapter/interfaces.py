from abc import ABC, abstractmethod


class IJuliaAdapter(ABC):
    @abstractmethod
    def execute_code(self, code: str, source_id: str) -> str:
        pass

    @abstractmethod
    def send_stdin(self, input_data: str) -> None:
        pass
