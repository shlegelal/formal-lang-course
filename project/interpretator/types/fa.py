from abc import ABC
from copy import copy
from pathlib import Path
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton as Nfa
from pyformlang.regular_expression import Regex

import networkx as nx

from project.interpretator.types.automata import GQLangAutomata
from project.interpretator.types.pair import GQLangPair
from project.interpretator.types.set import GQLangSet
from project.interpretator.types.triple import GQLangTriple
from project.utils.automata import dfa_by_regex, nfa_by_graph, intersect_nfa
from project.utils.binary_matrix import bm_by_nfa, transitive_closure
from project.utils.graph import get_graph


class GQLangFA(GQLangAutomata, ABC):
    def __init__(self, nfa: Nfa, t=None):
        self._nfa = nfa
        states = GQLangSet({s.value for s in nfa.states}, t)
        self._type = states.type

    @property
    def type(self):
        return self._type

    @property
    def nfa(self) -> Nfa:
        return self._nfa

    @classmethod
    def from_file(cls, path: Path) -> "GQLangFA":
        with open(path, "r") as f:
            graph = nx.drawing.nx_pydot.read_dot(f)
        return cls(nfa_by_graph(graph))

    @classmethod
    def from_str(cls, s: str) -> "GQLangFA":
        return cls(dfa_by_regex(Regex(s)))

    @classmethod
    def from_dataset(cls, s: str) -> "GQLangFA":
        return cls(nfa_by_graph(get_graph(s)))

    def set_starts(self, states: GQLangSet) -> "GQLangFA":
        if isinstance(None, states.type):
            states = GQLangSet({s.value for s in self._nfa.states})
        if self._type != states.type:
            raise TypeError(
                f"expected elements of type {self._type}, got {states.type}"
            )
        return GQLangFA(
            Nfa(
                states=copy(self._nfa.states),
                input_symbols=copy(self._nfa.symbols),
                start_state=states.items(),
                final_states=copy(self._nfa.final_states),
            )
        )

    def set_finals(self, states: GQLangSet) -> "GQLangFA":
        if isinstance(None, states.type):
            states = GQLangSet({s.value for s in self._nfa.states})
        if self._type != states.type:
            raise TypeError(
                f"expected elements of type {self._type}, got {states.type}"
            )
        return GQLangFA(
            Nfa(
                states=copy(self._nfa.states),
                input_symbols=copy(self._nfa.symbols),
                start_state=copy(self._nfa.start_states),
                final_states=states.items(),
            )
        )

    def add_starts(self, states: GQLangSet) -> "GQLangFA":
        if isinstance(None, states.type) and self._type != states.type:
            raise TypeError(
                f"expected elements of type {self._type}, got {states.type}"
            )
        return self.add_starts(states.items())

    def add_finals(self, states: GQLangSet) -> "GQLangFA":
        if isinstance(None, states.type) and self._type != states.type:
            raise TypeError(
                f"expected elements of type {self._type}, got {states.type}"
            )
        return self.add_finals(states.items())

    def starts(self) -> GQLangSet:
        return GQLangSet({s.value for s in self._nfa.start_states})

    def finals(self) -> GQLangSet:
        return GQLangSet({s.value for s in self._nfa.final_states})

    def nodes(self) -> GQLangSet:
        return GQLangSet({s.value for s in self._nfa.states})

    def labels(self) -> GQLangSet:
        return GQLangSet({s.value for s in self._nfa.symbols})

    def edges(self) -> GQLangSet:
        return GQLangSet(
            {
                GQLangTriple(s_from, label, s_to)
                for s_from, items in self._nfa.to_dict().items()
                for label, ss_to in items.items()
                for s_to in (ss_to if isinstance(ss_to, set) else {ss_to})
            }
        )

    def reachable(self) -> GQLangSet:
        reachable = set(
            GQLangPair(s.value, s.value)
            for s in self._nfa.start_states.intersection(self._nfa.final_states)
        )
        bm = bm_by_nfa(self._nfa)
        for n_from_i, n_to_i in zip(*transitive_closure(bm)):
            n_from = bm.states[n_from_i]
            n_to = bm.states[n_to_i]
            if n_from.is_start and n_to.is_final:
                reachable.add(GQLangPair(n_from.value, n_to.value))

        return GQLangSet(reachable)

    def intersect(self, other: GQLangAutomata) -> GQLangAutomata:
        if isinstance(other, GQLangFA):
            return GQLangFA(intersect_nfa(self._nfa, other.nfa))
        else:
            return other.intersect(self)

    def union(self, other: GQLangAutomata) -> GQLangAutomata:
        if self._type != other.type:
            raise TypeError(f"expected elements of type {self._type}, got {other.type}")
        if isinstance(other, GQLangFA):
            return GQLangFA(self._nfa.union(other._nfa).to_deterministic(), self._type)
        else:
            return other.union(self)

    def concat(self, other: GQLangAutomata) -> GQLangAutomata:
        if self._type != other.type:
            raise TypeError(f"expected elements of type {self._type}, got {other.type}")
        if isinstance(other, GQLangFA):
            return GQLangFA(
                self._nfa.concatenate(other._nfa).to_deterministic(), self._type
            )
        else:
            return other.concat(self)

    def star(self) -> "GQLangFA":
        return GQLangFA(self._nfa.kleene_star().to_deterministic())

    # def to_cfg(self) -> GQLangCFG:
    #     start_var = c.Variable("S")
    #     start_box = fa.NondeterministicFiniteAutomaton(
    #         states=copy(self._nfa.states),
    #         start_state=copy(self._nfa.start_states),
    #         final_states=copy(self._nfa.final_states),
    #     )
    #     for s_from, symb, s_to in iter_fa_transitions(self._nfa):
    #         start_box.add_transition(s_from, c.Terminal(symb.value), s_to)
    #     return Cfg(Rsm(start_var, {start_var: start_box}), self.meta.elem_meta)
