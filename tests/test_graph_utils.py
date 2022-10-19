import filecmp

from networkx import (
    algorithms,
    is_isomorphic,
)
from project.utils.graph_utils import *


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


# graph_info = get_graph_info("skos")
#
#
# def test_nodes_number():
#     assert graph_info.nodes_num == 144
#
#
# def test_edges_number():
#     assert graph_info.edges_num == 252
#
#
# def test_labels():
#     assert graph_info.labels == {
#         "seeAlso",
#         "comment",
#         "subPropertyOf",
#         "rest",
#         "type",
#         "creator",
#         "inverseOf",
#         "label",
#         "description",
#         "unionOf",
#         "domain",
#         "range",
#         "example",
#         "scopeNote",
#         "contributor",
#         "title",
#         "subClassOf",
#         "definition",
#         "first",
#         "disjointWith",
#         "isDefinedBy",
#     }


def test_raise_file_not_found_error():
    try:
        broken = get_graph_info_by_name("aaa")
        assert broken.nodes_num == "forty two"
    except FileNotFoundError:
        assert True
