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

        self.meta = {
            "target_compile_definitions": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
            "target_compile_features": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
            "target_compile_options": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
            "target_include_directories": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
            "target_link_directories": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
            "target_link_libraries": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
            "target_link_options": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
            "target_precompile_headers": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
            "target_sources": {
                Scope.PRIVATE: [],
                Scope.PUBLIC: [],
                Scope.INTERFACE: [],
            },
        }

    def __expand(self, ls) -> list:
        result = []
        for item in ls:
            if isinstance(item, list):
                result.extend(self.__expand(item))
            else:
                result.append(item)
        return result

    def add_sources(self, scope: Scope, *sources, allow_invaild=False):
        items = self.__expand(sources)
        assert allow_invaild or len(items) > 0 and \
            all(isinstance(item, Path)for item in items), \
            "Invalid call to add_source"
        self.meta["target_sources"][scope].extend(items)
        return self

    def add_includes(self, scope: Scope, *directories, allow_invaild=False):
        items = self.__expand(directories)
        assert allow_invaild or len(items) > 0 and \
            all(isinstance(item, Path)for item in items), \
            "Invalid call to add_include_directories"
        self.meta["target_include_directories"][scope].extend(items)
        return self

    def add_defines(self, scope: Scope, *definitions, allow_invaild=False):
        items = self.__expand(definitions)
        assert allow_invaild or len(items) > 0
        self.meta["target_compile_definitions"][scope].extend(items)
        return self

    def add_features(self, scope: Scope, *features, allow_invaild=False):
        items = self.__expand(features)
        assert allow_invaild or len(items) > 0
        self.meta["target_compile_features"][scope].extend(items)
        return self

    def add_options(self, scope: Scope, *options, allow_invaild=False):
        items = self.__expand(options)
        assert allow_invaild or len(items) > 0
        self.meta["target_compile_options"][scope].extend(items)
        return self

    def add_link_directories(self, scope: Scope, *directories, allow_invaild=False):
        items = self.__expand(directories)
        assert allow_invaild or len(items) > 0 and \
            all(isinstance(item, Path)for item in items), \
            "Invalid call to add_link_directories"
        self.meta["target_link_directories"][scope].extend(items)
        return self

    def add_link_libraries(self, scope: Scope, *libraries, allow_invaild=False):
        items = self.__expand(libraries)
        assert allow_invaild or len(items) > 0
        self.meta["target_link_libraries"][scope].extend(items)
        return self

    def add_link_options(self, scope: Scope, *options, allow_invaild=False):
        items = self.__expand(options)
        assert allow_invaild or len(items) > 0
        self.meta["target_link_options"][scope].extend(items)
        return self

    def add_precompile_headers(self, scope: Scope, *headers, allow_invaild=False):
        items = self.__expand(headers)
        assert allow_invaild or len(items) > 0
        self.meta["target_precompile_headers"][scope].extend(items)
        return self

    def _deal(self, item):
        if isinstance(item, str):
            return item
        elif isinstance(item, Path):
            return item.as_posix()
        else:
            raise ValueError(f"Invalid item: {item}")

    def to_cmake(self) -> str:
        if self.type == Type.EXECUTABLE:
            result = f"add_executable({self.name})\n"
        else:
            result = f"add_library({self.name} {self.type.value})\n"

        for part in self.meta:
            for scope in self.meta[part]:
                files = [
                    f'"{self._deal(item)}"' for item in self.meta[part][scope]
                ]
                if len(files) == 0:
                    continue
                result += f"{part}({self.name} {scope.value} {' '.join(files)})\n"

        return result
