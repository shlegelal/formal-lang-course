from pathlib import Path
import pytest
from pyformlang import cfg as c

from project.utils import cfg_utils
from load_test_res import load_test_res


def _assert_equal_cfgs(cfg0: c.CFG, cfg1: c.CFG):
    assert cfg0.start_symbol == cfg1.start_symbol
    assert cfg0.productions == cfg1.productions


@pytest.fixture
def cfg_file_path(request, tmp_path: Path) -> Path:
    cfg_text = request.param
    assert isinstance(cfg_text, str)

    path = tmp_path / "test_cfg.txt"
    with open(path, "w") as f:
        f.write(cfg_text)
    return path


@pytest.mark.parametrize(
    "cfg_file_path, start, expected",
    map(
        lambda d: (
            d[0],
            d[1],
            c.CFG.from_text(
                d[0],
                c.Variable(d[1]),
            )
            if d[1] is not None
            else c.CFG.from_text(d[0]),
        ),
        load_test_res("test_cfg_utils"),
    ),
    indirect=["cfg_file_path"],
)
def test_read_cfg(cfg_file_path: Path, start: str, expected: c.CFG):
    actual = (
        cfg_utils.read_cfg(cfg_file_path, start)
        if start is not None
        else cfg_utils.read_cfg(cfg_file_path)
    )

    _assert_equal_cfgs(actual, expected)


@pytest.mark.parametrize(
    "raw_cfg, start, expected",
    map(
        lambda d: (
            d[0],
            d[1],
            c.CFG.from_text(
                d[2],
                c.Variable(d[1]),
            )
            if d[1] is not None
            else c.CFG.from_text(d[2]),
        ),
        load_test_res("test_cfg_utils"),
    ),
)
def test_cfg_to_wcnf(raw_cfg: str, start: str, expected: c.CFG):
    actual = (
        cfg_utils.cfg_to_wcnf(raw_cfg, start)
        if start is not None
        else cfg_utils.cfg_to_wcnf(raw_cfg)
    )

    _assert_equal_cfgs(actual, expected)
