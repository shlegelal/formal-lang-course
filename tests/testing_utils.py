import inspect
import json
import pathlib
from collections.abc import Callable
from typing import TextIO
from typing import TypeVar

import networkx as nx
import pydot

_T = TypeVar("_T")


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
    transform: Callable[[dict], _T],
    *,
    data_filename: str | None = None,
    add_filename_suffix: bool = False,
) -> list[_T]:
    with _open_test_json(test_name, add_filename_suffix, data_filename) as f:
        test_datas = json.load(f)
    return [transform(test_data) for test_data in test_datas[test_name]]


def load_test_ids(
    test_name: str,
    *,
    data_filename: str | None = None,
    add_filename_suffix: bool = False,
) -> list[str]:
    with _open_test_json(test_name, add_filename_suffix, data_filename) as f:
        test_datas = json.load(f)
    return [test_data["description"] for test_data in test_datas[test_name]]


def dot_str_to_graph(dot: str) -> nx.Graph:
    return nx.drawing.nx_pydot.from_pydot(pydot.graph_from_dot_data(dot)[0])
