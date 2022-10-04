from pyformlang.finite_automaton import EpsilonNFA
from scipy.sparse import csr_array
from scipy.sparse import dok_array
from scipy.sparse import kron
from itertools import product
from typing import Any
from typing import NamedTuple


class BoolDecomposition:
    class StateInfo(NamedTuple):
        data: Any
        is_start: bool
        is_final: bool

    def __init__(
        self,
        states: list[StateInfo] | None = None,
        adjs: dict[Any, csr_array] | None = None,
    ):
        if states is not None and len(states) != len(set(states)):
            raise ValueError("States cannot contain duplicates")

        self.states: list[BoolDecomposition.StateInfo] = (
            states if states is not None else []
        )
        self.adjs: dict[Any, csr_array] = adjs if adjs is not None else {}

    @classmethod
    def from_nfa(
        cls, nfa: EpsilonNFA, sort_states: bool = False
    ) -> "BoolDecomposition":
        # Construct states, removing duplicates
        states = list(
            set(
                cls.StateInfo(
                    data=st.value,
                    is_start=st in nfa.start_states,
                    is_final=st in nfa.final_states,
                )
                for st in nfa.states
            )
        )
        if sort_states:
            states = sorted(states, key=lambda st: st.data)

        # Construct adjacency matrices
        adjs = {}
        transitions = nfa.to_dict()
        n = len(states)
        for n_from in transitions:
            for symbol, ns_to in transitions[n_from].items():
                adj = adjs.setdefault(symbol.value, dok_array((n, n)))
                beg_index = next(i for i, s in enumerate(states) if s.data == n_from)
                for n_to in ns_to if isinstance(ns_to, set) else {ns_to}:
                    end_index = next(i for i, s in enumerate(states) if s.data == n_to)
                    adj[beg_index, end_index] = 1
        # DOK is good for construction, CSR is good for calculations
        for key in adjs:
            adjs[key] = adjs[key].tocsr()

        return cls(states, adjs)

    def intersect(self, other: "BoolDecomposition") -> "BoolDecomposition":
        # Set of states of the intersection is the product of the given sets of states
        # State is "start" if both of its element states are "start"
        # State is "final" if both of its element states are "final"
        states = [
            self.StateInfo(
                data=(st1.data, st2.data),
                is_start=st1.is_start and st2.is_start,
                is_final=st1.is_final and st2.is_final,
            )
            for st1, st2 in product(self.states, other.states)
        ]

        # Set of symbols of the intersection is the union of the given sets of symbols
        # Adjacency matrix for a symbol is a kronecker product of the given matrices of
        # this symbol
        adjs = {}
        n = len(states)
        for symbol in set(self.adjs.keys()).union(set(other.adjs.keys())):
            if symbol in self.adjs and symbol in other.adjs:
                adjs[symbol] = kron(self.adjs[symbol], other.adjs[symbol], format="csr")
            else:
                adjs[symbol] = csr_array((n, n))

        return BoolDecomposition(states, adjs)

    def transitive_closure_any_symbol(self) -> tuple[list[int], list[int]]:
        # Gather all matrices to get all existing paths
        n = len(self.states)
        adj_all = sum(self.adjs.values(), start=csr_array((n, n)))
        # Remove explicit zeroes (just in case) to use nnz later
        adj_all.eliminate_zeros()

        # Transitive closure by repeated-squaring-like approach
        while True:
            # nnz gives the number of paths
            prev_path_num = adj_all.nnz
            # Multiplication gives new paths, while sum retains the old ones
            adj_all += adj_all @ adj_all
            # If no new paths appear, all paths have been discovered
            if prev_path_num == adj_all.nnz:
                break

        # Convert to a more user-friendly representation
        return adj_all.nonzero()
