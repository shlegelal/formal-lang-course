from collections import namedtuple
from project.grammar.ecfg import ECFG

RSM = namedtuple("RSM", "start boxes")


def rsm_from_ecfg(ecfg: ECFG) -> RSM:
    return RSM(
        ecfg.start,
        {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
    )


def minimize_rsm(rsm) -> RSM:
    for var, nfa in rsm.boxes.items():
        rsm.boxes[var] = nfa.minimize()
    return rsm
