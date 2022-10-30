from copy import deepcopy

import pytest
from pyformlang import cfg as c
from pyformlang.regular_expression import Regex

from load_test_res import load_test_res
from project.grammar.ecfg import ecfg_from_cfg
from project.grammar.rsm import rsm_from_ecfg, minimize_rsm


@pytest.mark.parametrize(
    "cfg",
    map(
        lambda res: c.CFG.from_text(res[0], res[1]),
        load_test_res("test_ecfg"),
    ),
)
def test_correct_ecfg(cfg):
    ecfg = ecfg_from_cfg(cfg)

    assert ecfg.variables == (
        cfg.variables
        if cfg.start_symbol is not None
        else (cfg.variables | {c.Variable("S")})
    )
    assert ecfg.terminals == cfg.terminals
    if cfg.start_symbol is not None:
        assert ecfg.start == cfg.start_symbol
    else:
        assert ecfg.start == c.Variable("S")


@pytest.mark.parametrize(
    "cfg, expected",
    map(
        lambda res: (
            c.CFG.from_text(res[0], res[1]),
            {c.Variable(pr[0]): Regex(pr[1]) for pr in res[2]},
        ),
        load_test_res("test_ecfg"),
    ),
)
def test_ecfg_productions(cfg, expected):
    ecfg = ecfg_from_cfg(cfg)

    assert len(ecfg.productions) == len(expected)
    for head in expected:
        actual_nfa = ecfg.productions[head].to_epsilon_nfa()
        expected_nfa = expected[head].to_epsilon_nfa()
        assert actual_nfa.is_equivalent_to(expected_nfa)


@pytest.mark.parametrize(
    "ecfg",
    map(
        lambda res: (
            ecfg_from_cfg(
                c.CFG.from_text(res[0], res[1])
                if res[1] is not None
                else c.CFG.from_text(res[0])
            )
        ),
        load_test_res("test_ecfg"),
    ),
)
def test_correct_rsm(ecfg):
    rsm = rsm_from_ecfg(ecfg)

    assert rsm.start == ecfg.start
    assert len(rsm.boxes) == len(ecfg.productions)
    for var in ecfg.productions:
        actual = rsm.boxes[var]
        expected = ecfg.productions[var].to_epsilon_nfa()
        assert actual.is_equivalent_to(expected)


@pytest.mark.parametrize(
    "rsm",
    map(
        lambda res: (
            rsm_from_ecfg(
                ecfg_from_cfg(
                    c.CFG.from_text(res[0], res[1])
                    if res[1] is not None
                    else c.CFG.from_text(res[0])
                )
            )
        ),
        load_test_res("test_ecfg"),
    ),
)
def test_minimize_rsm(rsm):
    actual = minimize_rsm(deepcopy(rsm))

    assert len(actual.boxes) == len(rsm.boxes)
    for var in rsm.boxes:
        assert actual.boxes[var].is_equivalent_to(rsm.boxes[var])
