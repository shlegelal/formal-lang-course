from abc import ABC, abstractmethod
from pathlib import Path

from project.interpretator.types.set import GQLangSet
from project.interpretator.types.type import GQLangType


class GQLangAutomata(GQLangType):
    @property
    @abstractmethod
    def type(self):
        ...

    @abstractmethod
    def from_file(self, path: Path) -> "GQLangAutomata":
        ...

    @abstractmethod
    def from_str(self, s: str) -> "GQLangAutomata":
        ...

    @abstractmethod
    def set_starts(self, states: GQLangSet) -> "GQLangAutomata":
        ...

    @abstractmethod
    def set_finals(self, states: GQLangSet) -> "GQLangAutomata":
        ...

    @abstractmethod
    def add_starts(self, states: GQLangSet) -> "GQLangAutomata":
        ...

    @abstractmethod
    def add_finals(self, states: GQLangSet) -> "GQLangAutomata":
        ...

    @property
    @abstractmethod
    def starts(self) -> GQLangSet:
        ...

    @property
    @abstractmethod
    def finals(self) -> GQLangSet:
        ...

    @property
    @abstractmethod
    def reachable(self) -> GQLangSet:
        ...

    @property
    @abstractmethod
    def labels(self) -> GQLangSet:
        ...

    @property
    @abstractmethod
    def edges(self) -> GQLangSet:
        ...

    @property
    @abstractmethod
    def nodes(self) -> GQLangSet:
        ...

    @abstractmethod
    def intersect(self, other: "GQLangAutomata") -> "GQLangAutomata":
        ...

    @abstractmethod
    def union(self, other: "GQLangAutomata") -> "GQLangAutomata":
        ...

    @abstractmethod
    def concat(self, other: "GQLangAutomata") -> "GQLangAutomata":
        ...
