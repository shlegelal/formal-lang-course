import pyformlang.finite_automaton as fa
from scipy.sparse import csr_array
from scipy.sparse import dok_array
from scipy.sparse import kron
from itertools import product
from typing import Any
from typing import TypeVar
from typing import NamedTuple

_Self = TypeVar("_Self")


class BoolDecomposition:
    class StateInfo(NamedTuple):
        data: Any
        is_start: bool
        is_final: bool

    states: list[StateInfo]
    adjs: dict[Any, csr_array]

    def __init__(
        self,
        states: list[StateInfo] | None = None,
        adjs: dict[Any, csr_array] | None = None,
    ):
        if states is not None and len(states) != len(set(states)):
            raise ValueError("States cannot contain duplicates")

        self.states = states if states is not None else []
        self.adjs = adjs if adjs is not None else {}

    @classmethod
    def from_nfa(cls, nfa: fa.EpsilonNFA, sort_states: bool = False) -> _Self:
        # Construct states, removing duplicates
        states = list(
            dict.fromkeys(
                cls.StateInfo(
                    data=st.value,
                    is_start=st in nfa.start_states,
                    is_final=st in nfa.final_states,
                )
                for st in nfa.states
            )
        )
        if sort_states is not None:
            states = sorted(states, key=lambda st: st.data)

        # Construct adjacency matrices
        adjs = {}
        transitions = nfa.to_dict()
        n = len(states)
        for beg in transitions:
            for symbol, ends in transitions[beg].items():
                adj = adjs.setdefault(symbol.value, dok_array((n, n)))
                beg_index = next(i for i, st in enumerate(states) if st.data == beg)
                for end in ends if isinstance(ends, set) else {ends}:
                    end_index = next(i for i, st in enumerate(states) if st.data == end)
                    adj[beg_index, end_index] = 1
        # DOK is good for construction, CSR is good for calculations
        for key in adjs:
            adjs[key] = adjs[key].tocsr()

        return cls(states, adjs)

    def intersect(self, other: _Self) -> _Self:
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
