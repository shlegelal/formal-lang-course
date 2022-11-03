import pytest
from pyformlang import cfg as c
from copy import deepcopy

from project.cfpq.ecfg import ECFG
from project.cfpq.rsm import RSM
from testing_utils import load_test_data
from testing_utils import load_test_ids
from testing_utils import dot_str_to_nfa
from testing_utils import are_equivalent


@pytest.mark.parametrize(
    "ecfg, expected",
    load_test_data(
        "test_rsm",
        lambda d: (
            ECFG.from_cfg(c.CFG.from_text(d["cfg"])),
            RSM(
                c.Variable(d["rsm"]["start"]),
                {
                    c.Variable(var): dot_str_to_nfa(nfa)
                    for var, nfa in d["rsm"]["boxes"].items()
                },
            ),
        ),
    ),
    ids=load_test_ids("test_rsm"),
)
class TestFromEcfg:
    def test_same_start(self, ecfg: ECFG, expected: RSM):
        actual = RSM.from_ecfg(ecfg)

        assert actual.start == expected.start

    def test_boxes_are_equivalent(self, ecfg: ECFG, expected: RSM):
        actual = RSM.from_ecfg(ecfg)

        assert len(actual.boxes) == len(expected.boxes)
        for var in expected.boxes:
            assert are_equivalent(actual.boxes[var], expected.boxes[var])


@pytest.mark.parametrize(
    "original",
    load_test_data(
        "test_rsm",
        lambda d: RSM.from_ecfg(ECFG.from_cfg(c.CFG.from_text(d["cfg"]))),
    ),
    ids=load_test_ids("test_rsm"),
)
def test_minimized_are_equivalent_to_original(original: RSM):
    minimized = deepcopy(original).minimize()

    assert len(minimized.boxes) == len(original.boxes)
    for var in original.boxes:
        assert are_equivalent(minimized.boxes[var], original.boxes[var])
