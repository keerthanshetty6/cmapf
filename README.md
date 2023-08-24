# CMAPF: MAPF utilities for clingo implemented in C++

Currently, this project computes reachable positions for the SoC optimization
given a MAPF problem.

See the examples folder for a simple application using the utilities.

## Installation

### For pypi packages

If our official pypi packages are used, install with:

```
pip install clingo cffi scikit-build
python setup.py build install
```

### Generic install

If clingo has been installed, the package can be compiled and installed using:

```
make
make intall
```

We recommend to install with conda as it provides the necessary clingo packages
and tools. Furthermore, the package will be installed in a separate environment
without interfering with the system.
