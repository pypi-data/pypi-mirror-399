from dataclasses import dataclass


@dataclass
class ChoiceRule:
    condition: str
    next_state: str
