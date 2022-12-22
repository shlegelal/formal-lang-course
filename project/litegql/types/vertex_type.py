import abc

from project.litegql.types.base_type import BaseType


# ABC inheritance actually does nothing, acting more as a remainder
class VertexType(BaseType, abc.ABC):
    pass
