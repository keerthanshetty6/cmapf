"""
A simple MAPF solver for the Soc criteria based on clingo.
"""

import sys
import timeit
from collections import defaultdict
from typing import Any, DefaultDict, List, Optional, Tuple

from clingo.application import Application, ApplicationOptions, Flag, clingo_main
from clingo.control import Control, Model
from clingo.symbol import Function, Number, Symbol

from cmapf import Objective, Problem, count_atoms


class MAPFApp(Application):
    """
    A simple MAPF solver for the Soc criteria.
    """

    # the delta value for the SoC objective
    _delta: Optional[int]
    # whether to compute reach atoms via cmapf or ASP
    _reach: Flag
    # whether to add per agent costs to models
    _cost: Flag
    # a dictionary to gather statistics
    _stats: dict
    # a mapping from agents to their shortest path lengths
    _sp: DefaultDict[Symbol, Symbol]
    # a list of literal and symbols for penalties
    _penalties: List[Tuple[int, Symbol]]

    def __init__(self):
        # the delta value to use
        # (None means a minimal value is computed)
        self._delta = None
        # whether to compute reachable positions with cmapf
        self._reach = Flag(True)
        # whether to compute per agent costs
        self._costs = Flag(True)
        # the statistics dictionary
        self._stats = {"Time": {}}
        # cached shortest paths/penalties
        self._sp = defaultdict(lambda: Number(0))
        self._penalties = None

    def _parse_delta(self, value: str):
        """
        Parse the delta value for the Soc Optimization.
        """
        if value == "auto":
            self._delta = None
            return True
        try:
            self._delta = int(value)
        except RuntimeError:
            return False

        return self._delta >= 0

    def _on_statistics(self, step, accu):
        """
        Add statistics.
        """
        stats = {"MAPF": self._stats}
        step.update(stats)
        accu.update(stats)

    def register_options(self, options: ApplicationOptions):
        """
        Register MAPF options.
        """
        options.add("MAPF", "delta", "set the delta value [auto]", self._parse_delta)
        options.add_flag(
            "MAPF", "reach", "compute reachable positions [True]", self._reach
        )
        options.add_flag(
            "MAPF", "show-costs", "add per agents costs to model [True]", self._costs
        )

    def _on_model(self, model: Model):
        """
        Add per agent costs to the model.
        """
        # precompute list of penalties
        if self._penalties is None:
            atoms = model.context.symbolic_atoms
            self._penalties = []
            for atom in atoms.by_signature("penalty", 2):
                agent, _ = atom.symbol.arguments
                self._penalties.append((atom.literal, agent))

        # add per agent costs to model
        costs: DefaultDict[Symbol, int] = defaultdict(lambda: 0)
        for literal, agent in self._penalties:
            if model.is_true(literal):
                costs[agent] += 1
        model.extend(
            [
                Function("cost", [agent, self._sp[agent], Number(cost)])
                for agent, cost in costs.items()
            ]
        )

    def main(self, ctl: Control, files) -> None:
        """
        The main function of the application.
        """
        # load files
        start = timeit.default_timer()
        for file in files:
            ctl.load(file)
        if not files:
            ctl.load("-")
        self._stats["Time"]["Load"] = timeit.default_timer() - start

        # ground instance in base program
        start = timeit.default_timer()
        ctl.ground()
        self._stats["Time"]["Ground Instance"] = timeit.default_timer() - start

        start = timeit.default_timer()
        problem = Problem(ctl)
        self._stats["Time"]["Extract Problem"] = timeit.default_timer() - start

        # either compute or use given delta
        if self._delta is None:
            start = timeit.default_timer()
            delta = problem.min_delta_or_horizon(Objective.SUM_OF_COSTS)
            self._stats["Time"]["Min Delta"] = timeit.default_timer() - start
        else:
            delta = self._delta

        # comute reachable locations
        parts = [("mapf", [Number(delta)])]
        if delta is None:
            # the problem is unsat because at least one agent cannot reach its goal
            res = False
        elif self._reach:
            # reachability computation via C++ has been requested
            start = timeit.default_timer()
            res = problem.add_reachable(ctl, Objective.SUM_OF_COSTS, delta)
            self._stats["Time"]["Reachable"] = timeit.default_timer() - start
        else:
            # reachability computation via ASP has been requested
            # (we still compute the shortest paths via C++)
            start = timeit.default_timer()
            res = problem.add_sp_length(ctl)
            self._stats["Time"]["Shortest Path"] = timeit.default_timer() - start
            parts.append(("reach", []))

        start = timeit.default_timer()
        if res:
            # ground the encoding
            ctl.ground(parts)
            self._stats["Reachable"] = count_atoms(ctl.symbolic_atoms, "reach", 3)

            # compute the minimum cost as the sum of the shortest path lengths
            min_cost = 0
            for atom in ctl.symbolic_atoms.by_signature("sp_length", 2):
                agent, length = atom.symbol.arguments
                self._sp[agent] = length
                min_cost += length.number
            self._stats["Min Cost"] = min_cost
        else:
            # make the problem unsatisfiable avoiding grounding
            with ctl.backend() as bck:
                bck.add_rule([])
        self._stats["Time"]["Ground Encoding"] = timeit.default_timer() - start

        if delta is not None:
            self._stats["Delta"] = delta

        # solve the MAPF problem
        kwargs: Any = {"on_statistics": self._on_statistics}
        if self._costs:
            kwargs["on_model"] = self._on_model
        ctl.solve(**kwargs)


clingo_main(MAPFApp(), sys.argv[1:])
