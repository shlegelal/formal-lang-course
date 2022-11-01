import pyformlang.cfg as c
from os import PathLike


def cfg_to_wcnf(cfg: str | c.CFG, start: str | None = None) -> c.CFG:
    if not isinstance(cfg, c.CFG):
        cfg = c.CFG.from_text(cfg, c.Variable(start if start is not None else "S"))
    tmp = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )
    new_productions = tmp._get_productions_with_only_single_terminals()
    new_productions = tmp._decompose_productions(new_productions)
    return c.CFG(start_symbol=cfg._start_symbol, productions=set(new_productions))


def read_cfg(path: PathLike, start: str = "S") -> c.CFG:
    with open(path, "r") as f:
        data = f.read()
    return c.CFG.from_text(data, c.Variable(start))
