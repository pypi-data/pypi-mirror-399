from dataclasses import dataclass

from ..components import Catcher, ItemProcessor, ItemReader, ResultWriter, Retry
from .base_state import State


@dataclass
class DistributedMap(State):
    type_ = "Map"
    item_processor: ItemProcessor
    item_reader: ItemReader
    items: list | None = None
    item_batcher: list | None = None
    max_concurrency: int | str | None = None
    tolerated_failure_pct: int | str | None = None
    tolerated_failure_count: int | str | None = None
    label: str | None = None
    result_writer: ResultWriter | None = None
    result_selector: dict | None = None
    retry: Retry | None = None
    catch: list[Catcher] | None = None


@dataclass
class Map(State):
    type_ = "Map"
    item_processor: ItemProcessor
    items: list | str | None = None
    item_selector: dict | None = None
    max_concurrency: int | str | None = None
    retry: Retry | None = None
    catch: list[Catcher] | None = None
