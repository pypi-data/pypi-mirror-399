import json
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any


def empty_list() -> list:
    """Returns an empty list."""
    return []


def empty_dict() -> dict:
    """Returns an empty dictionary."""
    return {}


class StateEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            obj_dict = asdict(obj)
            clean_obj_dict = {}
            for k, v in obj_dict.items():
                if k.endswith("_") and v is not None:
                    clean_obj_dict[k[0:-1].title().replace("_", "")] = v
                elif v is not None:
                    clean_obj_dict[k.title().replace("_", "")] = v
            return {clean_obj_dict.pop("Name"): clean_obj_dict}
        return super().default(obj)


@dataclass
class State:
    name: str
    type_: str | None = None  # usually set in __post_init__
    next_: str | None = None
    end_: bool | None = None
    comment: str | None = None
    assign: str | None = None
    output: Any = None
    query_language: str = "JSONata"

    def __post_init__(self) -> None:
        if self.end_ and self.next_ is not None:
            raise ValueError("If next_ is being used, end_ must be False.")
        return

    def to_json(self) -> str:
        return json.dumps(self, indent=4, cls=StateEncoder)
