from pathlib import Path
from .target import AbstractTarget
from .const import Generator
from ..const import PROJECT_NAME, BUILD_ROOT
import os
import subprocess


class Builder:
    def __init__(self, *, cmake: Path | None = None) -> None:
        """
        Args:
            - cmake: Path to cmake executable. If None, it will search for cmake in PATH.
        """
        self.targets = []

        self._cmake = cmake if cmake is not None else "cmake"
        self._check_cmake()

        self._name_set = set()

    def _check_cmake(self):
        result = subprocess.run(
            [self._cmake, "--version"],
            capture_output=True,
            shell=True,
            text=True,
        )
        assert result.returncode == 0, "CMake not found"
        stdout = result.stdout.strip()
        assert "cmake version" in stdout, "Invalid CMake"

    def attach(self, target: AbstractTarget):
        self.targets.append(target)

    def _gen_cmakelists_recursive(self, target: AbstractTarget):
        cmakelists = ""
        if target.built:
            return cmakelists

        assert target.name not in self._name_set, f"Duplicate target name: {target.name}"
        self._name_set.add(target.name)

        for dep in target._depend_on:
            cmakelists += self._gen_cmakelists_recursive(dep)
        cmakelists += f"# {target.name}\n"
        cmakelists += target.to_cmake()
        cmakelists += "\n"

        target.built = True
        return cmakelists

    def _gen_cmakelists(self, output_dir: Path):
        output_dir.mkdir(exist_ok=True)
        cmakelists = f"cmake_minimum_required(VERSION 3.15)\n"
        cmakelists += f"project({PROJECT_NAME})\n\n"

        for target in self.targets:
            cmakelists += self._gen_cmakelists_recursive(target)

        with open(output_dir / "CMakeLists.txt", 'w+') as f:
            f.write(cmakelists)

    def build(self, *, output_dir: Path = BUILD_ROOT, generator: Generator | None = None):
        self._gen_cmakelists(output_dir)
        cmd = [
            self._cmake,
            "-S",
            output_dir.as_posix(),
            "-B",
            output_dir.as_posix(),
        ]
        if generator is not None:
            cmd.extend(["-G", generator.value])

        res = subprocess.run(cmd, shell=True)
        assert res.returncode == 0, "CMake build failed"

        cmd = [self._cmake, "--build", output_dir.as_posix()]
        res = subprocess.run(cmd, shell=True)
        assert res.returncode == 0, "CMake build failed"
