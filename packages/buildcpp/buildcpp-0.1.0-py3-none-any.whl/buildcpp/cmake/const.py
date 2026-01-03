from enum import Enum


class Type(Enum):
    EXECUTABLE = 1
    STATIC_LIBRARY = 2
    SHARED_LIBRARY = 3
    MODULE_LIBRARY = 4
    OBJECT_LIBRARY = 5
    INTERFACE_LIBRARY = 6

    def __str__(self) -> str:
        if self == Type.EXECUTABLE:
            return "EXECUTABLE"
        elif self == Type.STATIC_LIBRARY:
            return "STATIC"
        elif self == Type.SHARED_LIBRARY:
            return "SHARED"
        elif self == Type.MODULE_LIBRARY:
            return "MODULE"
        elif self == Type.OBJECT_LIBRARY:
            return "OBJECT"
        elif self == Type.INTERFACE_LIBRARY:
            return "INTERFACE"
        assert False, 'Invalid type'


class Scope(Enum):
    PUBLIC = 1
    PRIVATE = 2
    INTERFACE = 3

    def __str__(self) -> str:
        if self == Scope.PUBLIC:
            return "PUBLIC"
        elif self == Scope.PRIVATE:
            return "PRIVATE"
        elif self == Scope.INTERFACE:
            return "INTERFACE"
        assert False, 'Invalid scope'
