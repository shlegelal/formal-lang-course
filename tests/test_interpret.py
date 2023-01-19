import inspect
from pathlib import Path

import pytest

from project.interpretator.interpreter import GQLang

DIR = Path(inspect.stack()[0].filename).parent / "interpret"


@pytest.mark.parametrize("path", sorted(DIR.glob("*.gql")))
def test_interpret(path: str):
    GQLang(path)
