from pathlib import Path
from .cmake.target import AbstractTarget


def import_project(buildcpp: Path) -> dict:
    """
    Import a third-party buildcpp project.

    If `buildcpp` is a directory, It will try to find a Python file
    with the same name as the folder in that folder.
    """
    if buildcpp.is_dir():
        buildcpp = buildcpp / (buildcpp.name + '.py')
    if not buildcpp.is_file():
        raise FileNotFoundError(f"Cannot find buildcpp project '{buildcpp}'")
    project_dir = buildcpp.parent
    project_name = project_dir.name.split('.')[0]

    import sys
    sys.path.insert(0, project_dir.as_posix())
    try:
        module = __import__(project_name)
    except ImportError:
        raise ImportError(f"Cannot import project '{buildcpp}'")
    finally:
        sys.path.remove(project_dir.as_posix())

    if not hasattr(module, 'export'):
        raise ImportError(
            f"Project '{buildcpp}' is not an importable project.")

    if isinstance(module.export, AbstractTarget):
        return {module.export.name: module.export}
    elif isinstance(module.export, list) and all(isinstance(t, AbstractTarget) for t in module.export):
        return {t.name: t for t in module.export}
    else:
        raise TypeError(f"Project '{buildcpp}' export is not a valid target.")
