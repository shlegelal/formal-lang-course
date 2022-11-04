import inspect
import json
import pathlib
from collections.abc import Callable
from typing import TextIO

import networkx as nx
from pyformlang import finite_automaton as fa
import pydot


def _open_test_json(
    test_name: str, add_filename_suffix: bool, filename: str | None = None
) -> TextIO:
    with pathlib.Path(inspect.stack()[2].filename) as f:
        parent = f.parent
        if filename is None:
            filename = f.stem
        if add_filename_suffix:
            filename += f"_{test_name}"
    return open(parent / "data" / f"{filename}.json")


def load_test_data(
    test_name: str,
    transform: Callable[[dict], tuple | list[tuple]],
    *,
    data_filename: str | None = None,
    add_filename_suffix: bool = False,
    is_aggregated: bool = False,
) -> list[tuple]:
    with _open_test_json(test_name, add_filename_suffix, data_filename) as f:
        test_datas = json.load(f)
    if not is_aggregated:
        return [transform(test_data) for test_data in test_datas[test_name]]
    else:
        res = []
        for test_data in test_datas[test_name]:
            res += transform(test_data)
        return res


def load_test_ids(
    test_name: str,
    *,
    data_filename: str | None = None,
    add_filename_suffix: bool = False,
    get_repeats: Callable[[dict], int] = lambda _: 1,
) -> list[str]:
    with _open_test_json(test_name, add_filename_suffix, data_filename) as f:
        test_datas = json.load(f)
    return [
        test_data["description"]
        for test_data in test_datas[test_name]
        for _ in range(get_repeats(test_data))
    ]


def dot_str_to_graph(dot: str) -> nx.Graph:
    return nx.drawing.nx_pydot.from_pydot(pydot.graph_from_dot_data(dot)[0])


def dot_str_to_nfa(dot: str) -> fa.EpsilonNFA:
    graph = dot_str_to_graph(dot)

    # Convert string-represented booleans in nodes from dot files
    for _, data in graph.nodes.data():
        if data["is_start"] in ("True", "False"):
            data["is_start"] = data["is_start"] == "True"
        if data["is_final"] in ("True", "False"):
            data["is_final"] = data["is_final"] == "True"
    # Convert string-represented epsilons in edges from dot files
    for _, _, data in graph.edges.data():
        if data["label"] == "epsilon":
            data["label"] = fa.Epsilon

    return fa.EpsilonNFA.from_networkx(graph)


def are_equivalent(
    fa1: fa.DeterministicFiniteAutomaton
    | fa.NondeterministicFiniteAutomaton
    | fa.EpsilonNFA,
    fa2: fa.DeterministicFiniteAutomaton
    | fa.NondeterministicFiniteAutomaton
    | fa.EpsilonNFA,
) -> bool:
    # pyformlang silently fails to check for equivalence automatas with no start state when minimized
    # But we can say such automatas are equivalent since they accept no words
    min1 = fa1.minimize()
    min2 = fa2.minimize()
    return (
        len(min1.start_states) == 0
        and len(min2.start_states) == 0
        or fa1.is_equivalent_to(fa2)
    )
