from abc import ABC
from dataclasses import dataclass, field

from src.application.executor_service.dto import CodeBlock, Priority


@dataclass(kw_only=True, frozen=True, slots=True)
class BaseCommand(ABC):
    priority: int

    def __lt__(self, other) -> bool:
        if isinstance(other, BaseCommand):
            return self.priority < other.priority

        return False


@dataclass(kw_only=True, frozen=True, slots=True)
class ExecuteCommand(BaseCommand):
    source_id: str
    block: CodeBlock
    priority: int = field(default=Priority.lowest.value)


@dataclass(kw_only=True, frozen=True, slots=True)
class StdinCommand(BaseCommand):
    source_id: str
    data: str
    priority: int = field(default=Priority.medium.value)
