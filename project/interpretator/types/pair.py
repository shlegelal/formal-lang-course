from project.interpretator.types.type import GQLangType


class GQLangPair(GQLangType):
    def __init__(self, s, f):
        if type(s) != type(f):
            raise TypeError("expected edge with nodes of same type")
        self._start = s
        self._final = f
        self._type = type(s)

    @property
    def start(self):
        return self._start

    @property
    def final(self):
        return self._final

    @property
    def type(self):
        return self._type

    @property
    def to_tuple(self):
        return self._start, self._final

    def __str__(self) -> str:
        return f"{self._start}->{self._final}"

    def __eq__(self, other: "GQLangPair") -> bool:
        return (
            self._start == other._start
            and self._final == other._final
            and self._label == other._label
        )

    def __hash__(self):
        return hash((self._start, self._final))
