import pytest
from pyformlang import cfg as c
from pyformlang import regular_expression as re

from project.cfpq.ecfg import ECFG
from testing_utils import load_test_data
from testing_utils import load_test_ids


@pytest.mark.parametrize(
    "cfg",
    load_test_data("test_ecfg", lambda d: c.CFG.from_text(d["cfg"], d["start"])),
    ids=load_test_ids("test_ecfg"),
)
class TestCompareECFGToCFG:
    def test_correct_variables(self, cfg: c.CFG):
        ecfg = ECFG.from_cfg(cfg)

        assert ecfg.variables == (
            cfg.variables
            if cfg.start_symbol is not None
            else (cfg.variables | {c.Variable("S")})
        )

    def test_correct_terminals(self, cfg: c.CFG):
        ecfg = ECFG.from_cfg(cfg)

        assert ecfg.terminals == cfg.terminals

    def test_correct_start(self, cfg: c.CFG):
        ecfg = ECFG.from_cfg(cfg)

        if cfg.start_symbol is not None:
            assert ecfg.start == cfg.start_symbol
        else:
            assert ecfg.start == c.Variable("S")


@pytest.mark.parametrize(
    "cfg, expected",
    load_test_data(
        "test_ecfg",
        lambda d: (
            c.CFG.from_text(d["cfg"], d["start"]),
            {
                c.Variable(p["head"]): re.Regex(p["body"])
                for p in d["expected_productions"]
            },
        ),
    ),
    ids=load_test_ids("test_ecfg"),
)
def test_equivalent_productions(cfg: c.CFG, expected: dict[c.Variable, re.Regex]):
    ecfg = ECFG.from_cfg(cfg)

    assert len(ecfg.productions) == len(expected)
    for head in expected:
        actual_nfa = ecfg.productions[head].to_epsilon_nfa()
        expected_nfa = expected[head].to_epsilon_nfa()
        assert actual_nfa.is_equivalent_to(expected_nfa)
