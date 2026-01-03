from dataclasses import dataclass
from typing import Any

from .base_state import State


@dataclass
class Succeed(State):
    type_ = "Succeed"
    output: Any = None

    def __post_init__(self) -> None:
        return super().__post_init__()


@dataclass
class Fail(State):
    type_ = "Fail"
    cause: Any = None
    error: Any = None

    def __post_init__(self) -> None:
        return super().__post_init__()
