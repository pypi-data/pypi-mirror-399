from pathlib import Path
from .target import AbstractTarget
from ..const import PROJECT_NAME, BUILD_ROOT
import os


class Builder:
    def __init__(self) -> None:
        self.targets = []

    def attach(self, target: AbstractTarget):
        self.targets.append(target)

    def _gen_cmakelists(self, output_dir: Path):
        output_dir.mkdir(exist_ok=True)
        cmakelists = f"cmake_minimum_required(VERSION 3.15)\n"
        cmakelists += f"project({PROJECT_NAME})\n"

        for target in self.targets:
            cmakelists += target.to_cmake()

        with open(output_dir / "CMakeLists.txt", 'w+') as f:
            f.write(cmakelists)

    def build(self, *, output_dir: Path = BUILD_ROOT):
        self._gen_cmakelists(output_dir)
        os.system(
            f"cmake -S {output_dir.as_posix()} -B {output_dir.as_posix()}")
        os.system(f"cmake --build {output_dir.as_posix()}")
