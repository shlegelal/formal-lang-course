from dataclasses import dataclass

from project.interpretator.types.pair import GQLangPair
from project.interpretator.types.triple import GQLangTriple


@dataclass
class Pattern:
    pass


@dataclass
class Wildcard(Pattern):
    pass


@dataclass
class Name(Pattern):
    name: str


@dataclass
class Unpair(Pattern):
    fst: Pattern
    snd: Pattern


@dataclass
class Untriple(Pattern):
    st: Pattern
    lab: Wildcard | Name
    fn: Pattern


def match(pat: Pattern, value) -> dict:
    match [pat, value]:
        case [Wildcard(), _]:
            return {}
        case [Name(name), _]:
            return {name: value}
        case [Unpair(fst_pat, snd_pat), elem]:
            fst_match = match(fst_pat, elem[0])
            snd_match = match(snd_pat, elem[1])
            return fst_match | snd_match
        case [Untriple(st_pat, lab_pat, fn_pat), elem]:
            fst_match = match(st_pat, elem[0])
            lab_pat = match(lab_pat, elem[1])
            snd_match = match(fn_pat, elem[2])
            return fst_match | lab_pat | snd_match
        case _:
            raise ValueError(f"Cannot match {pat} against {type(value)}")
