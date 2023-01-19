from abc import ABC
from pathlib import Path
import pyformlang.cfg as c

from project.interpretator.types.automata import GQLangAutomata
from project.interpretator.types.fa import GQLangFA
from project.interpretator.types.pair import GQLangPair
from project.interpretator.types.set import GQLangSet
from project.utils.cfg import read_cfg
from project.utils.ecfg import ecfg_by_cfg
from project.utils.rsm import rsm_by_ecfg, get_reachables


class GQLangCFG(GQLangAutomata, ABC):
    def __init__(self, cfg: c.CFG):
        self._cfg = cfg
        s = GQLangSet({v.value for v in cfg.variables})
        self._type = s.type
        self._rsm = rsm_by_ecfg(ecfg_by_cfg(cfg))

    def __str__(self):
        return self._cfg.to_text()

    @classmethod
    def from_str(cls, s: str) -> "GQLangCFG":
        return cls(c.CFG.from_text(s))

    @property
    def cfg(self) -> c.CFG:
        return self._cfg

    @property
    def type(self):
        return self._type

    @classmethod
    def from_file(cls, path: Path) -> "GQLangCFG":
        return cls(read_cfg(path))

    def set_starts(self, states: GQLangSet) -> "GQLangCFG":
        raise NotImplementedError("can't change CFG start symbols after creation")

    def set_finals(self, states: GQLangSet) -> "GQLangCFG":
        raise NotImplementedError("can't change CFG final symbols after creation")

    def add_starts(self, states: GQLangSet) -> "GQLangCFG":
        raise NotImplementedError("can't change CFG start symbols after creation")

    def add_finals(self, states: GQLangSet) -> "GQLangCFG":
        raise NotImplementedError("can't change CFG final symbols after creation")

    @property
    def starts(self) -> GQLangSet:
        return GQLangSet(
            {s.value for s in self._rsm.boxes[self._rsm.start].start_states}
        )

    @property
    def finals(self) -> GQLangSet:
        return GQLangSet(
            {s.value for s in self._rsm.boxes[self._rsm.start].final_states}
        )

    @property
    def reachable(self) -> GQLangSet:
        return GQLangSet(
            {GQLangPair(s1.value, s2.value) for (s1, s2) in get_reachables(self._rsm)}
        )

    @property
    def nodes(self) -> GQLangSet:
        return GQLangSet(
            {s.value for box in self._rsm.boxes.values() for s in box.states}
        )

    def intersect(self, other: GQLangAutomata) -> "GQLangCFG":
        if isinstance(other, GQLangFA):
            return GQLangCFG(self._cfg.intersection(other.nfa))
        raise TypeError(f"can't intersect CFG with another CFG")

    def concat(self, other: GQLangAutomata) -> "GQLangCFG":
        if isinstance(other, GQLangCFG):
            return GQLangCFG(self._cfg.concatenate(other.cfg))
        raise NotImplementedError(f"can't concat CFG with FA")

    def union(self, other: GQLangAutomata) -> "GQLangCFG":
        if isinstance(other, GQLangCFG):
            return GQLangCFG(self._cfg.union(other.cfg))
        raise NotImplementedError(f"can't union CFG with FA")
