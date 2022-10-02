import pytest
from pyformlang import finite_automaton as fa
from scipy.sparse import csr_array

from project.bool_decomposition import BoolDecomposition
from project.automata_utils import graph_to_nfa
from testing_utils import load_test_data
from testing_utils import dot_str_to_graph


def _dot_str_to_nfa(dot: str) -> fa.EpsilonNFA:
    graph = dot_str_to_graph(dot)

    start_states = set()
    for node, is_start in graph.nodes.data("is_start", default=False):
        if is_start == "True":
            start_states.add(node)

    final_states = set()
    for node, is_final in graph.nodes.data("is_final", default=False):
        if is_final == "True":
            final_states.add(node)

    return graph_to_nfa(graph, start_states, final_states)


def _dict_to_state_info(d: dict) -> BoolDecomposition.StateInfo:
    return BoolDecomposition.StateInfo(d["data"], d["is_start"], d["is_final"])


def _dict_to_adjs(d: dict[str, list[list[int]]]) -> dict[str, csr_array]:
    return {s: csr_array(l) for s, l in d.items()}


def _check_adjs_are_equal(adjs1: dict[str, csr_array], adjs2: dict[str, csr_array]):
    for (symbol1, adj1), (symbol2, adj2) in zip(
        sorted(adjs1.items()), sorted(adjs2.items())
    ):
        assert symbol1 == symbol2
        assert (adj1 - adj2).nnz == 0


class TestFromNfa:
    @pytest.mark.parametrize(
        "nfa, expected_states",
        load_test_data(
            "TestFromNfa",
            lambda d: (
                _dot_str_to_nfa(d["graph"]),
                [_dict_to_state_info(st) for st in d["expected_states"]],
            ),
            add_filename_suffix=True,
        ),
    )
    def test_states_are_correct(
        self, nfa: fa.EpsilonNFA, expected_states: list[BoolDecomposition.StateInfo]
    ):
        decomp = BoolDecomposition.from_nfa(nfa, sort_states=True)

        assert decomp.states == expected_states

    @pytest.mark.parametrize(
        "nfa, expected_adjs",
        load_test_data(
            "TestFromNfa",
            lambda d: (_dot_str_to_nfa(d["graph"]), _dict_to_adjs(d["expected_adjs"])),
            add_filename_suffix=True,
        ),
    )
    def test_adjs_are_correct(
        self, nfa: fa.EpsilonNFA, expected_adjs: dict[str, csr_array]
    ):
        decomp = BoolDecomposition.from_nfa(nfa, sort_states=True)

        _check_adjs_are_equal(decomp.adjs, expected_adjs)


class TestIntersect:
    @pytest.mark.parametrize(
        "states1, adjs1, states2, adjs2, expected_states",
        load_test_data(
            "TestIntersect",
            lambda d: (
                [_dict_to_state_info(st) for st in d["states1"]],
                _dict_to_adjs(d["adjs1"]),
                [_dict_to_state_info(st) for st in d["states2"]],
                _dict_to_adjs(d["adjs2"]),
                [
                    BoolDecomposition.StateInfo(
                        tuple(st["data"]), st["is_start"], st["is_final"]
                    )
                    for st in d["expected_states"]
                ],
            ),
            add_filename_suffix=True,
        ),
    )
    def test_states_are_correct(
        self,
        states1: list[BoolDecomposition.StateInfo],
        adjs1: dict[str, csr_array],
        states2: list[BoolDecomposition.StateInfo],
        adjs2: dict[str, csr_array],
        expected_states: list[BoolDecomposition.StateInfo],
    ):
        decomp1 = BoolDecomposition(states1, adjs1)
        decomp2 = BoolDecomposition(states2, adjs2)

        intersection = decomp1.intersect(decomp2)

        assert intersection.states == expected_states

    @pytest.mark.parametrize(
        "states1, adjs1, states2, adjs2, expected_adjs",
        load_test_data(
            "TestIntersect",
            lambda d: (
                [_dict_to_state_info(st) for st in d["states1"]],
                _dict_to_adjs(d["adjs1"]),
                [_dict_to_state_info(st) for st in d["states2"]],
                _dict_to_adjs(d["adjs2"]),
                _dict_to_adjs(d["expected_adjs"]),
            ),
            add_filename_suffix=True,
        ),
    )
    def test_adjs_are_correct(
        self,
        states1: list[BoolDecomposition.StateInfo],
        adjs1: dict[str, csr_array],
        states2: list[BoolDecomposition.StateInfo],
        adjs2: dict[str, csr_array],
        expected_adjs: dict[str, csr_array],
    ):
        decomp1 = BoolDecomposition(states1, adjs1)
        decomp2 = BoolDecomposition(states2, adjs2)

        intersection = decomp1.intersect(decomp2)

        _check_adjs_are_equal(intersection.adjs, expected_adjs)


class TestTransitiveClosureAnySymbol:
    @pytest.mark.parametrize(
        "adjs, expected_indices",
        load_test_data(
            "TestTransitiveClosureAnySymbol",
            lambda d: (
                _dict_to_adjs(d["adjs"]),
                {tuple(pair) for pair in d["expected_indices"]},
            ),
            add_filename_suffix=True,
        ),
    )
    def test_closure_is_correct(
        self, adjs: dict[str, csr_array], expected_indices: set[tuple]
    ):
        states_num = next(iter(adjs.values())).shape[0] if len(adjs) > 0 else 0
        states = [BoolDecomposition.StateInfo(i, True, True) for i in range(states_num)]
        decomp = BoolDecomposition(states, adjs)

        actual_indices = decomp.transitive_closure_any_symbol()

        assert set(zip(*actual_indices)) == expected_indices


class TestConstrainedBfs:
    @pytest.mark.parametrize(
        "main_states, main_adjs, constr_states, constr_adjs, expected",
        load_test_data(
            "TestConstrainedBfs",
            lambda d: (
                [_dict_to_state_info(st) for st in d["main_states"]],
                _dict_to_adjs(d["main_adjs"]),
                [_dict_to_state_info(st) for st in d["constr_states"]],
                _dict_to_adjs(d["constr_adjs"]),
                {end for _, end in d["expected"]},
            ),
            add_filename_suffix=True,
        ),
    )
    def test_not_separated(
        self,
        main_states: list[BoolDecomposition.StateInfo],
        main_adjs: dict[str, csr_array],
        constr_states: list[BoolDecomposition.StateInfo],
        constr_adjs: dict[str, csr_array],
        expected: set[int],
    ):
        main_decomp = BoolDecomposition(main_states, main_adjs)
        constraint_decomp = BoolDecomposition(constr_states, constr_adjs)

        actual = main_decomp.constrained_bfs(constraint_decomp)

        assert actual == expected

    @pytest.mark.parametrize(
        "main_states, main_adjs, constr_states, constr_adjs, expected",
        load_test_data(
            "TestConstrainedBfs",
            lambda d: (
                [_dict_to_state_info(st) for st in d["main_states"]],
                _dict_to_adjs(d["main_adjs"]),
                [_dict_to_state_info(st) for st in d["constr_states"]],
                _dict_to_adjs(d["constr_adjs"]),
                {(i, j) for i, j in d["expected"]},
            ),
            add_filename_suffix=True,
        ),
    )
    def test_separated(
        self,
        main_states: list[BoolDecomposition.StateInfo],
        main_adjs: dict[str, csr_array],
        constr_states: list[BoolDecomposition.StateInfo],
        constr_adjs: dict[str, csr_array],
        expected: set[tuple[int, int]],
    ):
        main_decomp = BoolDecomposition(main_states, main_adjs)
        constraint_decomp = BoolDecomposition(constr_states, constr_adjs)

        actual = main_decomp.constrained_bfs(constraint_decomp, separated=True)

        assert actual == expected
