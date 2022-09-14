import cfpq_data
import filecmp

from networkx import (
    algorithms,
    is_isomorphic,
)
from project.utils.graph_utils import (
    export_graph_to_dot,
    generate_labeled_two_cycles_graph,
)


def test_generate_labeled_two_cycles_graph():
    graph_expected = cfpq_data.labeled_two_cycles_graph(33, 22, labels=("fst", "snd"))
    graph_actual = generate_labeled_two_cycles_graph((33, 22), ("fst", "snd"))
    match_helper = algorithms.isomorphism.categorical_multiedge_match("label", None)
    assert is_isomorphic(graph_actual, graph_expected, edge_match=match_helper)


def test_export_graph():
    actual = cfpq_data.labeled_two_cycles_graph(3, 2, labels=("fst", "snd"))
    export_graph_to_dot(actual, "tests/res/actual_graph.dot")

    assert filecmp.cmp(
        "tests/res/actual_graph.dot",
        "tests/res/expected_graph.dot",
        shallow=False,
    )


def test_generate_and_export_graph():
    actual = generate_labeled_two_cycles_graph((3, 2), ("fst", "snd"))
    export_graph_to_dot(actual, "tests/res/actual_graph.dot")

    assert filecmp.cmp(
        "tests/res/actual_graph.dot",
        "tests/res/expected_graph.dot",
        shallow=False,
    )
