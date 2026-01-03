from dataclasses import dataclass

from .base_state import State


@dataclass
class Pass(State):
    type_ = "Pass"


@dataclass
class Wait(State):
    type_ = "Wait"
    seconds: int | None = None
    timestamp: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if (self.seconds is not None and self.timestamp is not None) or (
            self.seconds is None and self.timestamp is None
        ):
            raise ValueError("Exactly one of seconds and timestamp can be specified.")
