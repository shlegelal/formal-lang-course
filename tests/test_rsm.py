import pytest
from pyformlang import cfg as c
from copy import deepcopy

from project.cfpq.ecfg import ECFG
from project.cfpq.rsm import RSM
from testing_utils import load_test_data
from testing_utils import load_test_ids


@pytest.mark.parametrize(
    "ecfg",
    load_test_data(
        "test_cfg_utils",
        lambda d: (
            ECFG.from_cfg(
                c.CFG.from_text(d["cfg_text"], d["start"])
                if d["start"] is not None
                else c.CFG.from_text(d["cfg_text"])
            )
        ),
        data_filename="test_cfg_utils",
    ),
    ids=load_test_ids("test_cfg_utils", data_filename="test_cfg_utils"),
)
class TestFromEcfg:
    def test_same_start(self, ecfg: ECFG):
        rsm = RSM.from_ecfg(ecfg)

        assert rsm.start == ecfg.start

    def test_boxes_are_equivalent_to_productions(self, ecfg: ECFG):
        rsm = RSM.from_ecfg(ecfg)

        assert len(rsm.boxes) == len(ecfg.productions)
        for var in ecfg.productions:
            actual = rsm.boxes[var]
            expected = ecfg.productions[var].to_epsilon_nfa()
            assert actual.is_equivalent_to(expected)


@pytest.mark.parametrize(
    "rsm",
    load_test_data(
        "test_cfg_utils",
        lambda d: (
            RSM.from_ecfg(
                ECFG.from_cfg(
                    c.CFG.from_text(d["cfg_text"], d["start"])
                    if d["start"] is not None
                    else c.CFG.from_text(d["cfg_text"])
                )
            )
        ),
        data_filename="test_cfg_utils",
    ),
    ids=load_test_ids("test_cfg_utils", data_filename="test_cfg_utils"),
)
class TestMinimize:
    def test_minimized_are_equivalent_to_original(self, rsm: RSM):
        actual = deepcopy(rsm).minimize()

        assert len(actual.boxes) == len(rsm.boxes)
        for var in rsm.boxes:
            assert actual.boxes[var].is_equivalent_to(rsm.boxes[var])
