# CMAPF: MAPF utilities for clingo implemented in C++

Currently, this project computes reachable positions for the SoC optimization
given a MAPF problem.

See the examples folder for a simple application using the utilities.

## Installation

### For pypi packages

To use our official pypi packages, install with:

```
python -m venv venv
source venv/bin/activate
pip install .
```

Make sure that a recent enough C++ compiler is available on the system.

### Generic install

If clingo has been installed system wide, the package can be compiled and
installed using:

```
cmake -DCMAKE_BUILD_TYPE=release -DCMAKE_INSTALL_PREFIX=<prefix> -S . -B <build>
cmake --build <build>
cmake --install <build>
```

The `<build>` placeholder should be set to an arbitrary (empty) directory. We
recommend to install with [conda] as it provides the necessary clingo packages
and tools. In this case, the `<prefix>` placeholder can be set to
`$CONDA_PREFIX` to install into the active environment. This way, the package
does not interfere with the system. Please consult the [cmake] documentation
for further information.

**The bundled Makefile is only intended for development.**

[conda]: https://conda-forge.org/
[cmake]: https://cmake.org/documentation/
