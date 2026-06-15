
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import StrEnum, auto


class SourceType(StrEnum):
    SINGLE = auto()
    MULTIPLE = auto()


@dataclass
class Source(ABC):
    app: "AppSource" = field(repr=False)
    source: SourceType = None
    test_text: str = "Singletext utan source"

    @abstractmethod
    def set_to_multiple(self) -> None: ...

    @abstractmethod
    def set_to_single(self) -> None: ...


@dataclass
class MultipleSource(Source):
    source: SourceType = SourceType.MULTIPLE
    test_text: str = "Source för MULTIPLE"

    def set_to_multiple(self) -> None:
        print("Already in multiple")

    def set_to_single(self) -> None:
        self.app.set_source(SingleSource(self.app))


@dataclass
class SingleSource(Source):
    source: SourceType = SourceType.SINGLE
    test_text: str = "Source för SINGLE"

    def set_to_multiple(self) -> None:
        self.app.set_source(MultipleSource(self.app))

    def set_to_single(self) -> None:
        print("Already in single")


class AppSource:
    def __init__(self):
        self.source_type: Source = SingleSource(self)

    def set_source(self, source: Source):
        self.source_type = source

    def set_to_multiple(self) -> None:
        self.source_type.set_to_multiple()

    def set_to_single(self) -> None:
        self.source_type.set_to_single()

