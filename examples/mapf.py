"""
A simple MAPF solver based on clingo.
"""

import sys
import timeit
from collections import defaultdict
from typing import Any, DefaultDict, List, Optional, Sequence, Tuple

from clingo.application import Application, ApplicationOptions, Flag, clingo_main
from clingo.control import Control, Model
from clingo.symbol import Function, Number, Symbol

from cmapf import Objective, Problem, count_atoms


class MAPFApp(Application):
    """
    A simple MAPF solver.
    """

    # the delta value for the SoC objective
    _delta_or_horizon: Optional[int]
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
    # the objective to solve for
    _objective: Objective
    # the number of objectives given on the command line
    # (there will be an error if there is more than one)
    _objectives: int

    def __init__(self):
        self._delta_or_horizon = None
        self._reach = Flag(True)
        self._costs = Flag(True)
        self._stats = {"Time": {}}
        self._sp = defaultdict(lambda: Number(0))
        self._penalties = None
        self._objective = Objective.SUM_OF_COSTS
        self._objectives = 0

    def _parse_delta(self, value: str, objective: Objective):
        """
        Parse the delta or horizon value based on the criteria.
        """
        self._objective = objective
        self._objectives += 1
        if value == "auto":
            self._delta_or_horizon = None
            return True
        try:
            self._delta_or_horizon = int(value)
        except RuntimeError:
            return False

        return self._delta_or_horizon >= 0

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
        options.add(
            "MAPF",
            "delta",
            "set the delta value [auto]",
            lambda value: self._parse_delta(value, Objective.SUM_OF_COSTS),
        )
        options.add(
            "MAPF",
            "horizon",
            "set the horizon value",
            lambda value: self._parse_delta(value, Objective.MAKESPAN),
        )
        options.add_flag(
            "MAPF", "reach", "compute reachable positions [True]", self._reach
        )
        options.add_flag(
            "MAPF", "show-costs", "add per agents costs to model [True]", self._costs
        )

    def validate_options(self):
        """
        Validate options.
        """
        if self._objectives > 1:
            print("either a delta value or a horizon should be given")
            return False
        return True

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

    def _load(self, ctl: Control, files) -> Problem:
        """
        Load instance and encoding and then extract the MAPF problem.
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

        return problem

    def _prepare(
        self, ctl: Control, problem: Problem
    ) -> Optional[Sequence[Tuple[str, Sequence[Symbol]]]]:
        """
        Prepare for grounding and return the necessary parts to ground.
        """
        # either compute or use given delta/horizon
        if self._delta_or_horizon is None:
            start = timeit.default_timer()
            delta_or_horizon = problem.min_delta_or_horizon(self._objective)
            self._stats["Time"]["Min Delta"] = timeit.default_timer() - start
        else:
            delta_or_horizon = self._delta_or_horizon

        # the problem is unsat because at least one agent cannot reach its goal
        if delta_or_horizon is None:
            return None

        # select program parts based on objective
        parts: Any = [("mapf", [])]
        if self._objective == Objective.MAKESPAN:
            parts.extend([("makespan", [Number(delta_or_horizon)]), ("makespan", [])])
            self._stats["Horizon"] = delta_or_horizon
        else:
            parts.extend(
                [("sum_of_costs", [Number(delta_or_horizon)]), ("sum_of_costs", [])]
            )
            self._stats["Delta"] = delta_or_horizon

        # always add shortest paths
        if not self._reach or self._objective == Objective.MAKESPAN:
            start = timeit.default_timer()
            if not problem.add_sp_length(ctl):
                parts = None
            self._stats["Time"]["Shortest Path"] = timeit.default_timer() - start

        if self._reach:
            # reachability computation via C++ has been requested
            start = timeit.default_timer()
            if not problem.add_reachable(ctl, self._objective, delta_or_horizon):
                parts = None
            self._stats["Time"]["Reachable"] = timeit.default_timer() - start
        else:
            # reachability computation via ASP has been requested
            parts.append(("reach", []))

        return parts

    def _ground(
        self, ctl: Control, parts: Optional[Sequence[Tuple[str, Sequence[Symbol]]]]
    ) -> None:
        """
        Ground the MAPF encoding.
        """
        start = timeit.default_timer()
        if parts is not None:
            # ground the encoding
            ctl.ground(parts)
            self._stats["Reachable"] = count_atoms(ctl.symbolic_atoms, "reach", 3)

            # compute the minimum cost as the sum of the shortest path lengths
            min_cost = 0
            min_horizon = 0
            for atom in ctl.symbolic_atoms.by_signature("sp_length", 2):
                agent, length = atom.symbol.arguments
                self._sp[agent] = length
                min_cost += length.number
                min_horizon = max(min_horizon, length.number)

            self._stats["Min Cost"] = min_cost
            self._stats["Min Horizon"] = min_horizon
        else:
            # make the problem unsatisfiable avoiding grounding
            with ctl.backend() as bck:
                bck.add_rule([])
        self._stats["Time"]["Ground Encoding"] = timeit.default_timer() - start

    def _solve(self, ctl: Control) -> None:
        """
        Solve the MAPF problem.
        """
        kwargs: Any = {"on_statistics": self._on_statistics}
        if self._costs:
            kwargs["on_model"] = self._on_model
        ctl.solve(**kwargs)

    def main(self, ctl: Control, files) -> None:
        """
        The main function of the application.
        """
        problem = self._load(ctl, files)
        parts = self._prepare(ctl, problem)
        self._ground(ctl, parts)
        self._solve(ctl)


clingo_main(MAPFApp(), sys.argv[1:])
