from dataclasses import dataclass, field
from enum import Enum
from io import StringIO
from uuid import UUID


class Priority(Enum):
    highest = 1
    medium = 5
    lowest = 10


class Languages(Enum):
    JULIA = "jl"
    PYTHON = "py"
    MAGIC = "magic"


class CodeBlock:
    def __init__(
        self,
        language: Languages,
        code: str,
        block_id: str | None = None,
        index: int = 0,
        *,
        magic: bool = False
    ):
        self.magic = magic
        self.language = language
        self.index = index
        self.block_id = block_id
        self.__code = StringIO()
        self.__code.write(code)

    @property
    def code(self) -> str:
        return self.__code.getvalue()

    def append(self, *code: str) -> None:
        self.__code.write("\n".join(code))


@dataclass
class Task:
    source_id: str
    code_blocks: list[CodeBlock] = field(default_factory=list)
