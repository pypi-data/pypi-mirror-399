# buildcpp

![MIT-LICENSE](https://img.shields.io/github/license/Anglebase/buildcpp)
![PyPI](https://img.shields.io/pypi/v/buildcpp)

Buildcpp is an innovative build system that combines Python's expressive power with the reliability of CMake. You no longer need to deal with complex CMake syntax—simply manage your C++ projects using clear and maintainable Python code.

## Why buildcpp?

Setting up a C++ build process has traditionally been a tedious task. From Makefile to CMake and Xmake, developers have long sought ways to simplify building C++ projects. However, the inherent complexity of C++ builds remains. Buildcpp addresses this by using Python’s approachable syntax to write build scripts, while providing essential utilities for C++ project building.

## How It Works

Buildcpp serves the same role as CMake within the build system. Just as CMake scripts generate corresponding Makefiles when you run `cmake`, Buildcpp is designed to let you write Python scripts that, when executed, generate CMake scripts for the build process. This approach avoids reinventing the wheel and ensures Buildcpp is inherently cross-platform, leveraging the cross-platform nature of both Python and CMake.

## Getting Started

Buildcpp is essentially a Python package. First, ensure you have a [Python 3.7+](https://www.python.org/) environment installed on your system.

Run the following command in your terminal:

```shell
pip install buildcpp
```

Once installed, you’re ready to use Buildcpp.

For example, create a new directory for your C++ project and add a new Python file inside it. The folder and Python file names are not restricted—you can choose any name you prefer. Note that the Python file name will be used as the project name.

```text
myproject
└── myproject.py
```

Now you can add C++ source files as you normally would. Buildcpp does not impose any specific structure here. For instance, you might create a `src` folder to store `.cpp` files. Write a simple Hello World program in a C++ file. Your directory structure might look like this:

```text
myproject
├── myproject.py
└── src
    └── main.cpp
```

Next, write the Buildcpp build script:

```python
from buildcpp import *

target = Target('demo')\
    .add_source(Scope.PUBLIC, find_files(SRC_ROOT, '*.cpp'))

if __name__ == '__main__':
    builder = Builder()
    builder.attach(target)
    builder.build()
```

Here, we first create a `Target` object named `demo`. We then add source files to the target using the `add_source` method. The `Scope.PUBLIC` parameter indicates that these files are publicly accessible to other targets. The `find_files` function locates all `.cpp` files in the `src` directory.

We then create a `Builder` object, attach the target to it, and call the `build` method to generate the Makefile and compile the project.

For more detailed information, check out the [documentation](https://github.com/Anglebase/buildcpp/blob/master/docs/tutorial.md).

## LICENSE

MIT License
