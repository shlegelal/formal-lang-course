from project.interpretator.types.type import GQLangType


class GQLangSet(GQLangType):
    def __init__(self, s: set, t=None):
        if len(s) == 0:
            self._type = type(None)
        else:
            if t is None:
                iterator = iter(s)
                self._type = type(next(iterator))
                if not all(isinstance(v, self._type) for v in iterator):
                    raise TypeError("expected set with elements of same type")
            else:
                self._type = t
        self._set = s

    def __eq__(self, other: "GQLangSet") -> bool:
        if self._type != other._type:
            raise TypeError("expected sets with same type")
        return self._set == other._set

    def __str__(self):
        return "{" + ", ".join(str(v) for v in self._set) + "}"

    def __contains__(self, item) -> bool:
        if isinstance(item, self._type):
            raise TypeError(f"expected elements of type {self._type}")
        if isinstance(None, self._type) and item in self._set:
            return True
        return False

    def __hash__(self) -> int:
        return hash(self._set)

    def __len__(self) -> int:
        return len(self._set)

    @property
    def type(self):
        return self._type

    def items(self):
        return self._set
