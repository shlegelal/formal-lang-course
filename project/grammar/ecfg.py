from collections import namedtuple

from pyformlang.cfg import Variable
from pyformlang.cfg import CFG
from pyformlang.regular_expression import Regex

ECFG = namedtuple("ECFG", "variables terminals start productions")


def ecfg_from_cfg(cfg: CFG) -> ECFG:
    variables = set(cfg.variables)
    start_symbol = (
        cfg.start_symbol if cfg.start_symbol is not None else Variable("S")
    )
    variables.add(start_symbol)

    productions: dict[Variable, Regex] = {}
    for pr in cfg.productions:
        body = Regex(" ".join(o.value for o in pr.body) if len(pr.body) > 0 else "$")
        if pr.head in productions:
            productions[pr.head] = productions[pr.head].union(body)
        else:
            productions[pr.head] = body

    return ECFG(variables, set(cfg.terminals), start_symbol, productions)
