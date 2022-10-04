import json
import pathlib
import inspect
import pydot
import networkx as nx
from collections.abc import Callable
from typing import TypeVar

_T = TypeVar("_T")


def load_test_data(
    test_name: str, transform: Callable[[dict], _T], add_filename_suffix: bool = False
) -> list[_T]:
    with pathlib.Path(inspect.stack()[1].filename) as f:
        parent = f.parent
        filename = f.stem
        if add_filename_suffix:
            filename += f"_{test_name}"
    with open(parent / "data" / f"{filename}.json") as f:
        test_datas = json.load(f)
    return [transform(test_data) for test_data in test_datas[test_name]]


def dot_str_to_graph(dot: str) -> nx.Graph:
    return nx.drawing.nx_pydot.from_pydot(pydot.graph_from_dot_data(dot)[0])
