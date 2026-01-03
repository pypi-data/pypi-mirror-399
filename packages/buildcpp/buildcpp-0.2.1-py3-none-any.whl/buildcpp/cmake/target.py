from abc import ABC, abstractmethod
from .const import *
from pathlib import Path


def _expand(ls) -> list:
    result = []
    for item in ls:
        if isinstance(item, list):
            result.extend(_expand(item))
        else:
            result.append(item)
    return result


class AbstractTarget(ABC):
    """
    This abstract class is used for handling dependencies between projects.
    """

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name

        self._depend_on = []
        self.built = False

    @abstractmethod
    def to_cmake(self) -> str:
        pass

    def depend_on(self, *targets, allow_invaild=False):
        targets = _expand(targets)
        assert allow_invaild or len(targets) > 0 and \
            all(isinstance(target, AbstractTarget) for target in targets), \
            "Invalid call to depend_on"
        self._depend_on.extend(targets)
        return self

    def rename(self, new_name: str):
        self.name = new_name
        return self


class Target(AbstractTarget):
    """
    The standrad target in CMake.
    """

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
        self.link_libraries = []
        self.properties: dict[str, str | None] = {
            "C_STANDARD": None,
            "C_STANDARD_REQUIRED": None,
            "CXX_STANDARD": None,
            "CXX_STANDARD_REQUIRED": None,
        }

    def add_sources(self, scope: Scope, *sources, allow_invaild=False):
        items = _expand(sources)
        assert allow_invaild or len(items) > 0 and \
            all(isinstance(item, Path)for item in items), \
            "Invalid call to add_source"
        self.meta["target_sources"][scope].extend(items)
        return self

    def add_includes(self, scope: Scope, *directories, allow_invaild=False):
        items = _expand(directories)
        assert allow_invaild or len(items) > 0 and \
            all(isinstance(item, Path)for item in items), \
            "Invalid call to add_include_directories"
        self.meta["target_include_directories"][scope].extend(items)
        return self

    def add_defines(self, scope: Scope, *definitions, allow_invaild=False):
        items = _expand(definitions)
        assert allow_invaild or len(items) > 0
        self.meta["target_compile_definitions"][scope].extend(items)
        return self

    def add_compile_features(self, scope: Scope, *features, allow_invaild=False):
        items = _expand(features)
        assert allow_invaild or len(items) > 0
        self.meta["target_compile_features"][scope].extend(items)
        return self

    def add_compile_options(self, scope: Scope, *options, allow_invaild=False):
        items = _expand(options)
        assert allow_invaild or len(items) > 0
        self.meta["target_compile_options"][scope].extend(items)
        return self

    def add_link_directories(self, scope: Scope, *directories, allow_invaild=False):
        items = _expand(directories)
        assert allow_invaild or len(items) > 0 and \
            all(isinstance(item, Path)for item in items), \
            "Invalid call to add_link_directories"
        self.meta["target_link_directories"][scope].extend(items)
        return self

    def add_link_libraries(self, *libraries, allow_invaild=False):
        items = _expand(libraries)
        assert allow_invaild or len(items) > 0
        self.link_libraries.extend(items)
        return self

    def add_link_options(self, scope: Scope, *options, allow_invaild=False):
        items = _expand(options)
        assert allow_invaild or len(items) > 0
        self.meta["target_link_options"][scope].extend(items)
        return self

    def add_precompile_headers(self, scope: Scope, *headers, allow_invaild=False):
        items = _expand(headers)
        assert allow_invaild or len(items) > 0
        self.meta["target_precompile_headers"][scope].extend(items)
        return self

    def set_property(self, key: str, value: str):
        self.properties[key] = value
        return self

    def _deal(self, item):
        if isinstance(item, str):
            return item
        elif isinstance(item, Path):
            return item.as_posix()
        else:
            raise ValueError(f"Invalid item: {item}")

    def add_define(self, scope: Scope, key: str, value: str | None = None):
        define = key + (f"={value}" if value is not None else "")
        self.add_defines(scope, define)
        return self

    def c_standard(self, standard: int, required: bool = True):
        self.set_property("C_STANDARD", str(standard))
        self.set_property("C_STANDARD_REQUIRED", "ON" if required else "OFF")
        return self

    def cxx_standard(self, standard: int, required: bool = True):
        self.set_property("CXX_STANDARD", str(standard))
        self.set_property("CXX_STANDARD_REQUIRED", "ON" if required else "OFF")
        return self

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
                result += f"{part}({self.name} {scope.value}\n    {'\n    '.join(files)}\n)\n"

        link_libraries = [
            *self.link_libraries, *[dep.name for dep in self._depend_on]
        ]
        if len(link_libraries) > 0:
            result += f"target_link_libraries({self.name}\n    {'\n    '.join(link_libraries)}\n)\n"

        if any([prop is not None for prop in self.properties.values()]):
            result += f"set_target_properties({self.name} PROPERTIES\n"
            for key in self.properties:
                if self.properties[key] is not None:
                    result += f"    {key} {self.properties[key]}\n"
            result += ")\n"

        return result

    def __str__(self) -> str:
        return f"Target({self.name}, type={self.type.value})"