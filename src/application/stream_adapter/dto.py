from typing import Any

from pydantic import BaseModel


class StreamMessage(BaseModel):
    data: Any
