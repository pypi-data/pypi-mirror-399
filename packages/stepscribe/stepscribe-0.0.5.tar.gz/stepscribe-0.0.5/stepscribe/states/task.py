from dataclasses import dataclass, field

from ..components import Catcher, Retry
from .base_state import State, empty_dict


@dataclass
class Task(State):
    resource: str = ""
    arguments: dict = field(default_factory=empty_dict)
    credentials: str | None = None
    retry: list[Retry] | None = None
    catch: list[Catcher] | None = None
    timeout_seconds: int | None = None
    heartbeat_seconds: int | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        self.type_ = "Task"
        return
