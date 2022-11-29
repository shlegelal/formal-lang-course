from copy import deepcopy

import pytest
from pyformlang import cfg as c
from pyformlang.regular_expression import Regex
from pyformlang import finite_automaton as fa

from load_test_res import load_test_res
from project.grammar.ecfg import ecfg_from_cfg
from project.grammar.rsm import rsm_from_ecfg, minimize_rsm, RSM, bm_from_rsm
from test_automata_utils import build_graph_by_srt


def dot_str_to_nfa(dot: str):
    graph = build_graph_by_srt(dot)

    for _, data in graph.nodes.data():
        if data["is_start"] in ("True", "False"):
            data["is_start"] = data["is_start"] == "True"
        if data["is_final"] in ("True", "False"):
            data["is_final"] = data["is_final"] == "True"

    return fa.EpsilonNFA.from_networkx(graph)


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


@pytest.mark.parametrize(
    "rsm, expected_st, expected_starts, expected_finals",
    map(
        lambda r: (
            RSM(
                c.Variable("S"),
                {c.Variable(var): dot_str_to_nfa(nfa) for var, nfa in r[0].items()},
            ),
            r[1],
            r[2],
            r[3],
        ),
        load_test_res("test_rsm_to_bm"),
    ),
)
def test_rsm_to_bm(rsm: RSM, expected_st, expected_starts, expected_finals):
    bm = bm_from_rsm(rsm)
    states = bm.indexed_states.keys()
    for st in states:
        assert [st.value[0].value, st.value[1]] in expected_st

    for st in {st for st in states if bm.indexed_states[st] in bm.start_states}:
        assert [st.value[0].value, st.value[1]] in expected_starts

    for st in {st for st in states if bm.indexed_states[st] in bm.final_states}:
        assert [st.value[0].value, st.value[1]] in expected_finals
