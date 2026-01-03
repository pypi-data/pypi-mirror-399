from dataclasses import dataclass, field

from ..components.choice_rules import ChoiceRule
from .base_state import State, empty_list


@dataclass
class Choice(State):
    type: str = "Choice"
    choices: list[ChoiceRule] = field(default_factory=empty_list)
    default: str | None = None

    def __post_init__(self) -> None:
        return super().__post_init__()
