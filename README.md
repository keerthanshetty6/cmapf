# CMAPF: MAPF utilities for clingo implemented in C++

Currently, this project computes reachable positions for the SoC optimization
given a MAPF problem.

## Examples

```
$ python examples/example.py                   
edge(0,1) edge(1,2) edge(2,3) edge(2,4) start(a,0) start(b,2) goal(a,3) goal(b,4) shortest_path(a,3) shortest_path(b,1) reach(a,1,1) reach(a,1,2) reach(a,3,3) reach(a,3,4) reach(a,2,2) reach(a,2,3) reach(a,0,0) reach(a,0,1) reach(b,4,1) reach(b,4,2) reach(b,2,0) reach(b,2,1)
```

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
