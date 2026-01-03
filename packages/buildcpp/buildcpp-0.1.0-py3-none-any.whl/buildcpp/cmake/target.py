from abc import ABC, abstractmethod
from .const import *
from pathlib import Path


class AbstractTarget(ABC):
    """
    This abstract class is used for handling dependencies between projects.
    """
    name_set = set()

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name
        assert name not in AbstractTarget.name_set, f"Duplicate target name: {name}"

    @abstractmethod
    def to_cmake(self) -> str:
        pass


class Target(AbstractTarget):
    def __init__(self, name: str, type: Type = Type.EXECUTABLE) -> None:
        super().__init__(name)

        self.type = type

        self._sources: dict[Scope, list[Path]] = {}

    def __expand(self, ls) -> list:
        result = []
        for item in ls:
            if isinstance(item, list):
                result.extend(self.__expand(item))
            else:
                result.append(item)
        return result

    def add_source(self, scope: Scope, *sources):
        if scope not in self._sources:
            self._sources[scope] = []
        items = self.__expand(sources)
        assert len(items) > 0 and \
            all(isinstance(item, Path)for item in items), \
            "Invalid source files"
        self._sources[scope].extend(items)
        return self

    def to_cmake(self) -> str:
        result = f"add_executable({self.name})\n"
        for scope in self._sources:
            files = [f'"{item.as_posix()}"' for item in self._sources[scope]]
            result += f"target_sources({self.name} {str(scope)} {' '.join(files)})\n"

        return result
