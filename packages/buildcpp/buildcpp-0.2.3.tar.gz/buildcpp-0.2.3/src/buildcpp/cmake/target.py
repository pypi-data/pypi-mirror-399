from abc import ABC, abstractmethod
from .const import *
from pathlib import Path


def _expand(ls) -> list:
    """
    Expand the nested list into a single-layer list.
    """
    result = []
    for item in ls:
        if isinstance(item, list):
            result.extend(_expand(item))
        else:
            result.append(item)
    return result


class AbstractTarget(ABC):
    """
    This class is an extension interface for buildcpp.
    """

    def __init__(self, name: str) -> None:
        """
        Create a target instance with the name `name`.
        """
        super().__init__()

        self.name = name

        self._depend_on = []
        self.built = False

    @abstractmethod
    def to_cmake(self) -> str:
        """
        Rewrite this abstract method to define how to convert the target model to the CMake code.
        """
        pass

    def depend_on(self, *targets, allow_invaild=False):
        """
        Define the dependency relationships between targets.

        Indicates that the current target depends on all targets contained in `targets`.
        `allow_invaild` indicates whether the script should continue to run if it is not
        included in the `targets` list.
        """
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
        """
        Create a type `type` construction target with the name `name`.
        """
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
        """
        Add source files to the target.

        `scope` indicates the scope of the source files.
        `sources` is a list of source files.
        `allow_invaild` indicates whether the script should continue to run if `sources` is empty.
        """
        items = _expand(sources)
        assert allow_invaild or len(items) > 0, "Invalid call to add_sources"
        assert all(isinstance(i, Path) for i in items), "Invalid argument"
        self.meta["target_sources"][scope].extend(items)
        return self

    def add_includes(self, scope: Scope, *directories, allow_invaild=False):
        """
        Add include directories to the target.

        `scope` indicates the scope of the include directories.
        `directories` is a list of include directories.
        `allow_invaild` indicates whether the script should continue to run if `directories` is empty.
        """
        items = _expand(directories)
        assert allow_invaild or len(items) > 0, "Invalid call to add_includes"
        assert all(isinstance(i, Path) for i in items), "Invalid argument"
        self.meta["target_include_directories"][scope].extend(items)
        return self

    def add_defines(self, scope: Scope, *, allow_invaild=False, **defines):
        """
        Add preprocessor definitions to the target.

        `scope` indicates the scope of the definitions.
        `defines` is a dictionary of preprocessor definitions.
        `allow_invaild` indicates whether the script should continue to run if `definitions` is empty.
        """
        assert allow_invaild or len(defines) > 0, "Invalid call to add_defines"
        def check(d, i): return isinstance(d[i], str) or d[i] is None
        assert all(check(defines, i) for i in defines), "Invalid argument"
        def tostr(k, v): return f"{k}={v}" if v is not None else k
        items = [tostr(k, v) for k, v in defines.items()]
        self.meta["target_compile_definitions"][scope].extend(items)
        return self

    def add_compile_features(self, scope: Scope, *features, allow_invaild=False):
        """
        Add compile features to the target.

        `scope` indicates the scope of the features.
        `features` is a list of compile features.
        `allow_invaild` indicates whether the script should continue to run if `features` is empty.
        """
        items = _expand(features)
        assert allow_invaild or len(items) > 0
        self.meta["target_compile_features"][scope].extend(items)
        return self

    def add_compile_options(self, scope: Scope, *options, allow_invaild=False):
        """
        Add compile options to the target.

        `scope` indicates the scope of the options.
        `options` is a list of compile options.
        `allow_invaild` indicates whether the script should continue to run if `options` is empty.
        """
        items = _expand(options)
        assert allow_invaild or len(items) > 0
        self.meta["target_compile_options"][scope].extend(items)
        return self

    def add_link_directories(self, scope: Scope, *directories, allow_invaild=False):
        """
        Add link directories to the target.

        `scope` indicates the scope of the link directories.
        `directories` is a list of link directories.
        `allow_invaild` indicates whether the script should continue to run if `directories` is empty.
        """
        items = _expand(directories)
        assert allow_invaild or len(
            items) > 0, "Invalid call to add_link_directories"
        assert all(isinstance(i, Path) for i in items), "Invalid argument"
        self.meta["target_link_directories"][scope].extend(items)
        return self

    def add_link_libraries(self, *libraries, allow_invaild=False):
        """
        Add link libraries to the target.

        `libraries` is a list of link libraries.
        `allow_invaild` indicates whether the script should continue to run if `libraries` is empty.
        """
        items = _expand(libraries)
        assert allow_invaild or len(items) > 0
        self.link_libraries.extend(items)
        return self

    def add_link_options(self, scope: Scope, *options, allow_invaild=False):
        """
        Add link options to the target.

        `scope` indicates the scope of the options.
        `options` is a list of link options.
        `allow_invaild` indicates whether the script should continue to run if `options` is empty.
        """
        items = _expand(options)
        assert allow_invaild or len(items) > 0
        self.meta["target_link_options"][scope].extend(items)
        return self

    def add_precompile_headers(self, scope: Scope, *headers, allow_invaild=False):
        """
        Add precompile headers to the target.

        `scope` indicates the scope of the headers.
        `headers` is a list of precompile headers.
        `allow_invaild` indicates whether the script should continue to run if `headers` is empty.
        """
        items = _expand(headers)
        assert allow_invaild or len(items) > 0
        self.meta["target_precompile_headers"][scope].extend(items)
        return self

    def set_properties(self, **kwargs):
        """
        Set a property of the target.

        `kwargs` is a dictionary of properties.
        """
        for key in kwargs:
            self.properties[key] = kwargs[key]
        return self

    def _deal(self, item):
        if isinstance(item, str):
            return item
        elif isinstance(item, Path):
            return item.as_posix()
        else:
            raise ValueError(f"Invalid item: {item}")

    def c_standard(self, standard: int, required: bool = True):
        """
        Set the C standard of the target.

        `standard` is the C standard to be used.
        `required` indicates whether the C standard is required.
        """
        self.set_properties(C_STANDARD=str(standard))
        self.set_properties(C_STANDARD_REQUIRED="ON" if required else "OFF")
        return self

    def cxx_standard(self, standard: int, required: bool = True):
        """
        Set the C++ standard of the target.

        `standard` is the C++ standard to be used.
        `required` indicates whether the C++ standard is required.
        """
        self.set_properties(CXX_STANDARD=str(standard))
        self.set_properties(CXX_STANDARD_REQUIRED="ON" if required else "OFF")
        return self

    def to_cmake(self) -> str:
        """
        Rewrite this method to define how to convert the target model to the CMake code.
        """
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
        """
        Format the target as a string.
        """
        return f"Target({self.name}, type={self.type.value})"
