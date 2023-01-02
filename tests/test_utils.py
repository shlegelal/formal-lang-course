import json
import pathlib
import inspect
import pydot
from networkx import drawing, MultiDiGraph, is_isomorphic, isomorphism
from pyformlang import finite_automaton as fa


def load_test_res(test_name: str) -> list[tuple[dict, dict]]:
    with pathlib.Path(inspect.stack()[1].filename) as f:
        parent = f.parent
        filename = f.stem
    with open(parent / "res" / f"{filename}.json") as f:
        raw_res = json.load(f)
    res = list(
        map(
            lambda case: tuple(case.values())
            if len(case) > 1
            else next(iter(case.values())),
            raw_res[test_name],
        )
    )
    return res


def build_graph_by_srt(s: str) -> MultiDiGraph:
    return drawing.nx_pydot.from_pydot(pydot.graph_from_dot_data(s)[0])


def _string_to_bool_from_dot(graph):
    for _, data in graph.nodes.data():
        if data["is_start"] in ("True", "False"):
            data["is_start"] = data["is_start"] == "True"
        if data["is_final"] in ("True", "False"):
            data["is_final"] = data["is_final"] == "True"

    return graph


def is_isomorphic_fa_and_graph(f: fa.FiniteAutomaton, graph: MultiDiGraph) -> bool:
    fa_graph = f.to_networkx()
    # Remove nodes extra added by pyformlang
    for node in list(fa_graph):
        if isinstance(node, str) and node.endswith("_starting"):
            fa_graph.remove_node(node)
    # Convert string to bool from dot file
    fa_graph = _string_to_bool_from_dot(fa_graph)

    return is_isomorphic(
        fa_graph,
        graph,
        edge_match=isomorphism.categorical_edge_match("label", None),
    )


def dot_str_to_nfa(dot: str):
    graph = build_graph_by_srt(dot)

    graph = _string_to_bool_from_dot(graph)

    return fa.EpsilonNFA.from_networkx(graph)


def nfa_by_transactions(
    transitions_list: list[tuple], start_states: set = None, final_states: set = None
) -> fa.NondeterministicFiniteAutomaton:
    res = fa.NondeterministicFiniteAutomaton()

    if not len(transitions_list):
        return res

    res.add_transitions(transitions_list)
    for state in start_states:
        res.add_start_state(fa.State(state))
    for state in final_states:
        res.add_final_state(fa.State(state))

    return res
