import pytest
from pyformlang import cfg as c

from project.algorithms.cyk import cyk
from test_utils import load_test_res


@pytest.mark.parametrize(
    "cfg, words",
    map(
        lambda d: (
            c.CFG.from_text(d[0]),
            d[1],
        ),
        load_test_res("test_cyk"),
    ),
)
def test_cyk_equal_pyformlang(cfg, words):
    assert all(cyk(cfg, word) == cfg.contains(word) for word in words)


@pytest.mark.parametrize(
    "cfg, words, accepts",
    map(
        lambda d: (
            c.CFG.from_text(d[0]),
            d[1],
            d[2],
        ),
        load_test_res("test_cyk"),
    ),
)
def test_cyk_accepts(cfg, words, accepts):
    assert all((cyk(cfg, words[i]) == accepts[i] for i in range(len(words))))
