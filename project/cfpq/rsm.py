from pyformlang.cfg import Variable
from pyformlang.finite_automaton import EpsilonNFA

from project.cfpq.ecfg import Ecfg


class Rsm:
    def __init__(self, start: Variable, boxes: dict[Variable, EpsilonNFA]):
        self.start = start
        self.boxes = boxes

    @classmethod
    def from_ecfg(cls, ecfg: Ecfg):
        return cls(
            ecfg.start,
            {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
        )

    def minimize(self) -> "Rsm":
        for var, nfa in self.boxes.items():
            self.boxes[var] = nfa.minimize()
        return self
