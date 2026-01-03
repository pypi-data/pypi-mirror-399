import sys
from pathlib import Path


def _get_root_dir() -> tuple[Path, str]:
    main = sys.modules['__main__']
    assert main.__file__ is not None, "Internal error: no __file__ attribute in __main__ module"
    path = Path(main.__file__).absolute()
    root_dir = path.parent
    name = path.name.split('.')[0]
    return root_dir, name


PROJECT_ROOT, PROJECT_NAME = _get_root_dir()  # Project root directory
BUILD_ROOT = Path(PROJECT_ROOT) / 'build'  # Build directory
SRC_ROOT = Path(PROJECT_ROOT) / 'src'  # Source directory
