from pathlib import Path
from .target import AbstractTarget
from .const import Generator
from ..const import PROJECT_NAME, BUILD_ROOT
from .target import _expand
import subprocess


class Builder:
    """
    The builder is responsible for generating CMake scripts and executing the build.
    """
    def __init__(self, *, cmake: Path | None = None) -> None:
        """
        `cmake` is used to indicate the path where the CMake executable file is located.
        If it is `None`, an attempt will be made to search for it in the system's
        environment variables.
        """
        self.targets = []

        self._cmake = cmake if cmake is not None else "cmake"
        self._check_cmake()

        self._name_set = set()

    def _check_cmake(self):
        """
        Check if the CMake is valid.
        """
        result = subprocess.run(
            [self._cmake, "--version"],
            capture_output=True,
            shell=True,
            text=True,
        )
        assert result.returncode == 0, "CMake not found"
        stdout = result.stdout.strip()
        assert "cmake version" in stdout, "Invalid CMake"

    def attach(self, *targets, allow_invaild=False):
        """
        Use the targets included in the `targets` as the targets to be built by the builder.
        `allow_invaild` indicates whether the target should continue to run if it is not
        included in the `targets` list.
        """
        targets = _expand(targets)
        assert allow_invaild or len(targets) > 0, "No target specified"
        assert all(isinstance(t, AbstractTarget) for t in targets), "Invalid target"
        self.targets.extend(targets)

    def _gen_cmakelists_recursive(self, target: AbstractTarget):
        """
        Generate the CMakeLists.txt file for the target and its dependencies.
        """
        cmakelists = ""
        # Check if the target has already been built.
        if target.built:
            return cmakelists

        # Check for duplicate target names.
        assert target.name not in self._name_set, f"Duplicate target name: {target.name}"
        self._name_set.add(target.name)

        # Generate the CMakeLists.txt file for the target and its dependencies.
        for dep in target._depend_on:
            cmakelists += self._gen_cmakelists_recursive(dep)
        cmakelists += f"# {target.name}\n"
        cmakelists += target.to_cmake()
        cmakelists += "\n"

        # Mark the target as built.
        target.built = True
        return cmakelists

    def _gen_cmakelists(self, output_dir: Path):
        """
        Generate the CMakeLists.txt file for the targets and their dependencies.
        """
        # Create the output directory if it does not exist.
        output_dir.mkdir(exist_ok=True)

        # Generate the CMakeLists.txt file.
        cmakelists = f"cmake_minimum_required(VERSION 3.15)\n"
        cmakelists += f"project({PROJECT_NAME})\n\n"
        for target in self.targets:
            cmakelists += self._gen_cmakelists_recursive(target)

        # Write the CMakeLists.txt file to the output directory.
        with open(output_dir / "CMakeLists.txt", 'w+') as f:
            f.write(cmakelists)

    def build(self, *, output_dir: Path = BUILD_ROOT, generator: Generator | None = None):
        """
        Instruct to start the construction process. `output_dir` indicates the
        directory where the build is located, which by default is the build
        directory in the root directory of the project. `generator` indicates
        the generator to be used, and if not specified, it is determined by CMake.
        """
        # Generate the CMakeLists.txt file.
        self._gen_cmakelists(output_dir)

        # Generate the makefiles.
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

        # Build the project.
        cmd = [self._cmake, "--build", output_dir.as_posix()]
        res = subprocess.run(cmd, shell=True)
        assert res.returncode == 0, "CMake build failed"
