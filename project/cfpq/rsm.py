from collections.abc import Set as AbstractSet
from copy import deepcopy
from pathlib import Path
from typing import Callable

import networkx as nx
import pydot
import pyformlang.cfg as c
import pyformlang.finite_automaton as fa

from project.cfpq.ecfg import Ecfg
from project.rpq.fa_utils import concat_fas
from project.rpq.fa_utils import ConcreteFA
from project.rpq.fa_utils import iter_fa_transitions
from project.rpq.fa_utils import star_fa
from project.rpq.fa_utils import union_fas
from project.utils.bool_decomposition import BoolDecomposition


class Rsm:
    def __init__(self, start: c.Variable, boxes: dict[c.Variable, fa.EpsilonNFA]):
        self.start = start
        self.boxes = boxes

    @classmethod
    def from_cfg(cls, cfg: c.CFG, start_index: int = 0) -> "Rsm":
        """Preserves Terminals and Variables in the labels of the resulting boxes."""
        last_state = fa.State(start_index)  # Ensure no overlapping for correct union
        boxes: dict[c.Variable, fa.NondeterministicFiniteAutomaton] = {}
        # Sort to get determined results
        for p in sorted(cfg.productions, key=str):
            nfa = fa.NondeterministicFiniteAutomaton()
            nfa.add_start_state(last_state)
            for obj in p.body:
                if isinstance(obj, c.Epsilon):
                    continue
                next_state = fa.State(last_state.value + 1)
                nfa.add_transition(last_state, obj, next_state)
                last_state = next_state
            # Not checking for emptiness because pyformlang treats empty as epsilon
            nfa.add_final_state(last_state)
            last_state = fa.State(last_state.value + 1)
            if p.head in boxes:
                boxes[p.head] = union_fas(boxes[p.head], nfa)
            else:
                boxes[p.head] = nfa
        if cfg.start_symbol not in boxes:
            boxes[cfg.start_symbol] = fa.NondeterministicFiniteAutomaton(
                start_state={last_state}
            )
        return cls(start=cfg.start_symbol or c.Variable("S"), boxes=boxes)

    @classmethod
    def from_ecfg(cls, ecfg: Ecfg) -> "Rsm":
        return cls(
            ecfg.start,
            {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
        )

    @classmethod
    def from_dot_file(cls, path: Path) -> "Rsm":
        g = pydot.graph_from_dot_file(path)[0]

        start_var = c.Variable(g.get_name())

        boxes: dict[c.Variable, fa.NondeterministicFiniteAutomaton] = {}
        for subg in g.get_subgraph_list():
            var = c.Variable(subg.get_name())

            subg = nx.drawing.nx_pydot.from_pydot(subg)
            nfa = fa.NondeterministicFiniteAutomaton(
                states=set(subg.nodes),
                start_state=set(subg.nodes),
                final_states=set(subg.nodes),
            )
            for pred, succ, symb in subg.edges.data("label", default=""):
                lab = c.Variable(symb) if symb.isupper() else c.Terminal(symb)
                nfa.add_transition(pred, lab, succ)

            if var in boxes:
                boxes[var] = union_fas(boxes[var], nfa)
            else:
                boxes[var] = nfa

        # Ensure a correct start box always exist
        if start_var not in boxes:
            boxes[start_var] = fa.NondeterministicFiniteAutomaton(start_state={0})

        return cls(start_var, boxes)

    def minimize(self) -> "Rsm":
        for var, box in self.boxes.items():
            self.boxes[var] = box.minimize()
        return self

    def add_starts(self, starts: AbstractSet) -> "Rsm":
        box = self.boxes[self.start]
        for s in starts:
            box.add_start_state(s)
        return self

    def add_finals(self, finals: AbstractSet) -> "Rsm":
        box = self.boxes[self.start]
        for s in finals:
            box.add_final_state(s)
        return self

    def set_starts(self, starts: AbstractSet) -> "Rsm":
        box = self.boxes[self.start]
        self.boxes[self.start] = type(box)(
            states=box.states,
            input_symbols=box.symbols,
            transition_function=box._transition_function,
            start_state=starts,
            final_states=box.final_states,
        )
        return self

    def set_finals(self, finals: AbstractSet) -> "Rsm":
        box = self.boxes[self.start]
        self.boxes[self.start] = type(box)(
            states=box.states,
            input_symbols=box.symbols,
            transition_function=box._transition_function,
            start_state=box.start_states,
            final_states=finals,
        )
        return self

    def get_starts(self) -> set[fa.State]:
        return self.boxes[self.start].start_states

    def get_finals(self) -> set[fa.State]:
        return self.boxes[self.start].final_states

    def get_states(self) -> set[fa.State]:
        return {s for box in self.boxes.values() for s in box.states}

    def get_transitions(self) -> set[tuple[fa.State, fa.Symbol, fa.State]]:
        return {
            (s_from, symb, s_to)
            for box in self.boxes.values()
            for s_from, symb, s_to in iter_fa_transitions(box)
        }

    def get_reachables(self) -> set[tuple[fa.State, fa.State]]:
        # First remove all variable transitions as they may actually be non-terminable
        # (e.g. have no finishes or always lead to infinite recursion) and then
        # gradually add them back until no new transitions appear

        decomp = BoolDecomposition.from_rsm(self)
        nonterminatable_adjs = {}
        res = set()

        # Initialize non-terminable transitions explicitly handling start-final nodes in
        # case they will not appear in transitive closures
        for var in set(self.boxes).union(decomp.adjs):
            if not isinstance(var, c.Variable):
                continue
            start_finals = (
                self.boxes[var].start_states.intersection(self.boxes[var].final_states)
                if var in self.boxes
                else set()
            )
            if len(start_finals) == 0 and var in decomp.adjs:
                nonterminatable_adjs[var] = decomp.adjs.pop(var)
            if var == self.start:
                res |= {(s, s) for s in start_finals}

        # Iteratively compute transitive closures and add new variable transitions
        while True:
            old_len = len(nonterminatable_adjs)

            transitive_closure_indices = zip(*decomp.transitive_closure_any_symbol())
            for n_from_i, n_to_i in transitive_closure_indices:
                n_from = decomp.states[n_from_i]
                n_to = decomp.states[n_to_i]
                if n_from.is_start and n_to.is_final:
                    var1, s1 = n_from.data
                    var2, s2 = n_to.data
                    assert var1 == var2
                    if var1 in nonterminatable_adjs:
                        decomp.adjs[var1] = nonterminatable_adjs.pop(var1)
                    if var1 == self.start:
                        res.add((fa.State(s1), fa.State(s2)))

            if len(nonterminatable_adjs) == old_len:
                break

        return res

    def intersect(self, nfa: fa.EpsilonNFA, swapped: bool = False) -> "Rsm":
        # TODO: apply tensor CFPQ to NFA, then intersect and interpret the result
        #  somehow
        raise NotImplementedError()

    @staticmethod
    def _suffixed_boxes(
        boxes: dict[c.Variable, ConcreteFA], suffix: int
    ) -> dict[c.Variable, ConcreteFA]:
        def suffixed_box(box: ConcreteFA) -> ConcreteFA:
            new_box = type(box)(
                start_state=deepcopy(box.start_states),
                final_states=deepcopy(box.final_states),
            )
            for s_from, symb, s_to in iter_fa_transitions(box):
                new_box.add_transition(
                    s_from,
                    c.Variable((symb.value, suffix))
                    if isinstance(symb.value, c.Variable)
                    else symb,
                    s_to,
                )
            return new_box

        return {
            c.Variable((var.value, suffix)): suffixed_box(box)
            for var, box in boxes.items()
        }

    def _combine(
        self,
        other: "Rsm",
        get_start_box: Callable[[fa.EpsilonNFA, fa.EpsilonNFA], fa.EpsilonNFA],
    ) -> "Rsm":
        # Make variables distinctive
        fst_boxes = self._suffixed_boxes(self.boxes, 1)
        snd_boxes = self._suffixed_boxes(other.boxes, 2)

        # Construct the start box
        new_start = c.Variable("S")
        start_box = get_start_box(
            fst_boxes[c.Variable((self.start, 1))],
            snd_boxes[c.Variable((other.start, 2))],
        )

        return Rsm(new_start, {new_start: start_box} | fst_boxes | snd_boxes)

    def concat(self, other: "Rsm") -> "Rsm":
        return self._combine(other, concat_fas)

    def union(self, other: "Rsm") -> "Rsm":
        return self._combine(other, union_fas)

    def star(self) -> "Rsm":
        boxes = self._suffixed_boxes(self.boxes, 1)
        boxes[c.Variable("S")] = star_fa(boxes[c.Variable((self.start, 1))])
        return Rsm(self.start, boxes)
