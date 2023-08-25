import sys
import timeit
from collections import defaultdict

from clingo.application import Application, ApplicationOptions, Flag, clingo_main
from clingo.control import Control, Model
from clingo.symbol import Function, Number

import cmapf


class MAPFApp(Application):
    def __init__(self):
        # the delta value to use
        # (None means a minimal value is computed)
        self._delta = None
        # whether to compute reachable positions with cmapf
        self._reach = Flag(True)
        # whether to compute per agent costs
        self._costs = Flag(True)
        # whether to add number of reachable positions to statistics
        # (Python is slow, so we can avoid even this loop)
        self._show_reach = Flag(True)
        # the statistics dictionary
        self._stats = {"Time": {}}

    def _parse_delta(self, value: str):
        if value == "auto":
            self._delta = None
            return True
        try:
            self._delta = int(value)
        except RuntimeError:
            return False

        return self._delta >= 0

    def _on_statistics(self, step, accu):
        stats = {"MAPF": self._stats}
        step.update(stats)
        accu.update(stats)

    def register_options(self, options: ApplicationOptions):
        options.add("MAPF", "delta", "set the delta value [auto]", self._parse_delta)
        options.add_flag(
            "MAPF", "reach", "compute reachable positions [True]", self._reach
        )
        options.add_flag(
            "MAPF", "show-costs", "add per agents costs to model [True]", self._costs
        )
        options.add_flag(
            "MAPF", "show-reach", "add number of reachable nodes to statistics [True]", self._show_reach
        )

    def _on_model(self, model: Model):
        # add per agent costs to model
        sp = {}
        costs = defaultdict(lambda: 0)
        for atom in model.symbols(atoms=True):
            if atom.match("sp_length", 2):
                agent, length = atom.arguments
                sp[agent] = length
            if atom.match("penalty", 2):
                agent, _ = atom.arguments
                costs[agent] += 1
        model.extend([Function("cost", [agent, sp[agent], Number(cost)]) for agent, cost in costs.items()])

    def main(self, ctl: Control, files):
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

        # either compute or use given delta
        if self._delta is None:
            start = timeit.default_timer()
            delta = cmapf.compute_min_delta(ctl)
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
            res = cmapf.add_reachable(ctl, delta)
            self._stats["Time"]["Reachable"] = timeit.default_timer() - start
        else:
            # reachability computation via ASP has been requested
            # (we still compute the shortest paths via C++)
            start = timeit.default_timer()
            res = cmapf.add_sp_length(ctl)
            self._stats["Time"]["Shortest Path"] = timeit.default_timer() - start
            parts.append(("reach", []))

        start = timeit.default_timer()
        if res:
            # ground the encoding
            ctl.ground(parts)
            if self._show_reach:
                reach = ctl.symbolic_atoms.by_signature("reach", 3)
                self._stats["Reachable"] = sum(1 for _ in reach)
        else:
            # make the problem unsatisfiable avoiding grounding
            with ctl.backend() as bck:
                bck.add_rule([])
        self._stats["Time"]["Ground Encoding"] = timeit.default_timer() - start

        if delta is not None:
            self._stats["Delta"] = delta

        # solve the MAPF problem
        kwargs = {"on_statistics": self._on_statistics}
        if self._costs:
            kwargs["on_model"] = self._on_model
        ctl.solve(**kwargs)


clingo_main(MAPFApp(), sys.argv[1:])
