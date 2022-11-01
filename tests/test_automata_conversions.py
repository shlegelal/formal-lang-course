import networkx as nx
import pytest
from pyformlang import finite_automaton as fa

from project.rpq import fa_utils
from project.utils import graph_utils
from testing_utils import dot_str_to_graph
from testing_utils import dot_str_to_nfa
from testing_utils import are_equivalent
from testing_utils import load_test_data
from testing_utils import load_test_ids


class TestRegexToMinDfa:
    @pytest.mark.parametrize(
        "raw_regex, expected",
        load_test_data(
            "TestRegexToMinDfa.test_regex_converts_to_correct_dfa",
            lambda d: (
                d["raw_regex"],
                dot_str_to_nfa(d["expected_dfa_dot"]).to_deterministic(),
            ),
        ),
        ids=load_test_ids("TestRegexToMinDfa.test_regex_converts_to_correct_dfa"),
    )
    def test_regex_converts_to_correct_dfa(
        self, raw_regex: str, expected: fa.DeterministicFiniteAutomaton
    ):
        actual = fa_utils.regex_to_min_dfa(raw_regex)

        assert are_equivalent(actual, expected)


class TestGraphToNfa:
    @pytest.mark.parametrize(
        "graph, start_states, final_states, expected",
        load_test_data(
            "TestGraphToNfa.test_on_predefined_graph",
            lambda d: (
                dot_str_to_graph(d["graph"]),
                d["start_states"],
                d["final_states"],
                dot_str_to_nfa(d["expected_nfa_graph"]),
            ),
        ),
        ids=load_test_ids("TestGraphToNfa.test_on_predefined_graph"),
    )
    def test_on_predefined_graph(
        self,
        graph: nx.Graph,
        start_states: set | None,
        final_states: set | None,
        expected: fa.EpsilonNFA,
    ):
        actual = fa_utils.graph_to_nfa(graph, start_states, final_states)

        assert are_equivalent(actual, expected)

    @pytest.mark.parametrize(
        "first_cycle_num, second_cycle_num",
        load_test_data(
            "TestGraphToNfa.test_on_synthetic_graph",
            lambda d: (d["first_cycle_num"], d["second_cycle_num"]),
        ),
        ids=load_test_ids("TestGraphToNfa.test_on_synthetic_graph"),
    )
    def test_on_synthetic_graph(self, first_cycle_num: int, second_cycle_num: int):
        expected_graph = graph_utils.build_labeled_two_cycles_graph(
            first_cycle_num, "a", second_cycle_num, "b"
        )

        nfa = fa_utils.graph_to_nfa(expected_graph, set(), set())

        # Not testing start and final as already tested on predefined graphs
        assert nx.is_isomorphic(
            nfa.to_networkx(),
            expected_graph,
            edge_match=nx.isomorphism.categorical_edge_match("label", None),
        )

    @pytest.mark.parametrize(
        "dataset_graph_name",
        load_test_data(
            "TestGraphToNfa.test_on_dataset_graph", lambda d: d["dataset_graph_name"]
        ),
        ids=load_test_ids("TestGraphToNfa.test_on_dataset_graph"),
    )
    def test_on_dataset_graph(self, dataset_graph_name: str):
        expected_graph = graph_utils.load_graph_from_cfpq_data(dataset_graph_name)

        nfa = fa_utils.graph_to_nfa(expected_graph, set(), set())

        # Not testing start and final as already tested on predefined graphs
        assert nx.is_isomorphic(
            nfa.to_networkx(),
            expected_graph,
            edge_match=nx.isomorphism.categorical_edge_match("label", None),
        )
