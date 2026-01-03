from dataclasses import dataclass, field

from ..components import Catcher, Retry
from ..state_machine import StateMachine
from .base_state import State, empty_list


@dataclass
class Parallel(State):
    branches: list[StateMachine] = field(default_factory=empty_list)
    arguments: str | None = None
    retry: Retry = None
    catch_: list[Catcher] | None = None

    def __post_init__(self) -> None:
        return super().__post_init__()
