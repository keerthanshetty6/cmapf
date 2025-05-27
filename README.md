# Heuristics based priority for MAPF

## Installation

### To use the pypi packages 

```
python -m venv camp
camp\Scripts\activate
pip install .
```

# camp is the virtual environment name

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
