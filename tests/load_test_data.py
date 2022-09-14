import json
import pathlib
import inspect


def load_test_data(test_name: str) -> list[tuple[dict, dict]]:
    with pathlib.Path(inspect.stack()[1].filename) as f:
        parent = f.parent
        filename = f.stem
    with open(parent / "data" / f"{filename}.json") as f:
        raw_data = json.load(f)
    data = list(map(lambda case: tuple(case.values()), raw_data[test_name]))
    return data
