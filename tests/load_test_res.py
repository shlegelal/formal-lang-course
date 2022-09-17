import json
import pathlib
import inspect


def load_test_res(test_name: str) -> list[tuple[dict, dict]]:
    with pathlib.Path(inspect.stack()[1].filename) as f:
        parent = f.parent
        filename = f.stem
    with open(parent / "res" / f"{filename}.json") as f:
        raw_res = json.load(f)
    res = list(
        map(
            lambda case: tuple(case.values()) if len(case) > 1 else next(iter(case.values())),
            raw_res[test_name],
        )
    )
    return res
