"""
MAPF utilities for clingo written in C++.
"""

from enum import IntEnum
from typing import Optional

from clingo._internal import _handle_error
from clingo.control import Control
from clingo.symbolic_atoms import SymbolicAtoms

from ._cmapf import ffi as _ffi
from ._cmapf import lib as _lib

__all__ = ["version", "Objective", "Problem", "count_atoms"]


def version():
    """
    The CMAPF version number.
    """
    p_major = _ffi.new("int*")
    p_minor = _ffi.new("int*")
    p_revision = _ffi.new("int*")
    _lib.cmapf_version(p_major, p_minor, p_revision)
    return p_major[0], p_minor[0], p_revision[0]


class Objective(IntEnum):
    """
    The available MAPF objectives.
    """

    SUM_OF_COSTS = _lib.cmapf_objective_sum_of_costs
    MAKESPAN = _lib.cmapf_objective_makespan


class Problem:
    """
    A MAPF problem.
    """

    def __init__(self, ctl: Control):
        """
        Create a MAPF problem instance initializing it from the facts in the
        given control object.

        Facts over start/2, goal/2, and edge/2 are used for initialization.
        """
        rep = _ffi.new("cmapf_problem_t**")
        _handle_error(
            _lib.cmapf_problem_construct(rep, _ffi.cast("clingo_control_t*", ctl._rep))
        )
        self._rep = rep[0]

    def __del__(self):
        _lib.cmapf_problem_destroy(self._rep)

    def min_delta_or_horizon(self, objective: Objective) -> Optional[int]:
        """
        Compute the minimal delta or horizon for which the given MAPF problem
        is not trivially unsatisfiable.

        For the sum of costs objective this is a delta value and for the
        makespan objective this is a horizon.

        If the MAPF problem is detected to be unsatisfiable returns None.
        """
        res = _ffi.new("bool*")
        delta = _ffi.new("int*")
        _handle_error(
            _lib.cmapf_problem_min_delta_or_horizon(self._rep, objective, res, delta)
        )
        if res[0]:
            return delta[0]
        return None

    def add_sp_length(self, ctl: Control) -> bool:
        """
        Compute the shortest path length from start to goal for each agent.

        The function returns false if there is no shortest path for some agent.

        Atoms over predicate sp_length/2 are added to the problem. Atom
        sp_length(A,L) indicates that agent A can reach its goal within L time
        steps from its start ignoring any collisions with other agents.
        """
        res = _ffi.new("bool*")
        _handle_error(
            _lib.cmapf_problem_add_sp_length(
                self._rep, _ffi.cast("clingo_control_t*", ctl._rep), res
            )
        )
        return res[0]

    def add_reachable(
        self, ctl: Control, objective: Objective, delta_or_horizon: int
    ) -> bool:
        """
        Compute an approximation of reachable nodes assuming limited moves of
        the agents.

        The function returns false if there is an agent that cannot reach its
        goal.

        For the sum of costs objective, an agent can only move for the first n
        time points, where n is the length of its shortest path from start to
        goal plus the given delta.

        For the makespan objective, an agent can move during the given horizon.

        The function assumes that the control object already holds a MAPF
        problem in standard form.

        Atoms over the predicates reach/3 and sp_length/2 are added to the
        control object.

        Atoms reach(A,U,T) are added to the control object indicating that an
        agent A can reach a node U at time point T. For the sum of costs
        objective, there is an implicit call to add_sp_length also adding atoms
        over sp_length/2.
        """
        res = _ffi.new("bool*")
        _handle_error(
            _lib.cmapf_problem_add_reachable(
                self._rep,
                _ffi.cast("clingo_control_t*", ctl._rep),
                objective,
                delta_or_horizon,
                res,
            )
        )
        return res[0]


def count_atoms(syms: SymbolicAtoms, name: str, arity: int):
    """
    Count the number of atoms over the given signature.

    The idea here is that counting in C++ is much faster than in Python.
    """
    res = _ffi.new("int*")
    _handle_error(
        _lib.cmapf_count_atoms(
            _ffi.cast("clingo_symbolic_atoms_t*", syms._rep), name.encode(), arity, res
        )
    )
    return res[0]


__version__ = ".".join(str(num) for num in version())
