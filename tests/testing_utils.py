import json
import pathlib
import inspect
import pydot
import networkx as nx


def load_test_data(test_name: str) -> list[tuple]:
    with pathlib.Path(inspect.stack()[1].filename) as f:
        parent = f.parent
        filename = f.stem
    with open(parent / "data" / f"{filename}.json") as f:
        raw_data = json.load(f)
    data = list(
        map(
            lambda case: tuple(case.values())
            if len(case) > 1
            else next(iter(case.values())),
            raw_data[test_name],
        )
    )
    return data


def dot_str_to_graph(dot: str) -> nx.Graph:
    return nx.drawing.nx_pydot.from_pydot(pydot.graph_from_dot_data(dot)[0])
