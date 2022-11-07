from pathlib import Path
import pyformlang.cfg as c


def cfg_to_wcnf(cfg: str | c.CFG, start: str = "S") -> c.CFG:
    if not isinstance(cfg, c.CFG):
        cfg = c.CFG.from_text(cfg, c.Variable(start))
    tmp = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )
    new = tmp._get_productions_with_only_single_terminals()
    new = tmp._decompose_productions(new)
    return c.CFG(start_symbol=cfg._start_symbol, productions=set(new))


def read_cfg(path: Path, start: str = "S") -> c.CFG:
    with open(path, "r") as f:
        data = f.read()
    return c.CFG.from_text(data, c.Variable(start))
