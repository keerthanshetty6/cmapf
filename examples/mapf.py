import sys
import timeit
from collections import defaultdict

from clingo.application import Application, ApplicationOptions, Flag, clingo_main
from clingo.control import Control, Model
from clingo.symbol import Function, Number

import cmapf


class MAPFApp(Application):
    def __init__(self):
        self._delta = None
        self._reach = Flag(True)
        self._costs = Flag(True)
        self._show_reach = Flag(True)
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
        costs = defaultdict(lambda: 0)
        for atom in model.symbols(atoms=True):
            if atom.match("sp_length", 2):
                agent, length = atom.arguments
                costs[agent] += length.number
            if atom.match("costs", 2):
                agent, _ = atom.arguments
                costs[agent] += 1
        model.extend([Function("cost", [agent, Number(cost)]) for agent, cost in costs.items()])

    def main(self, ctl: Control, files):
        start = timeit.default_timer()
        for file in files:
            ctl.load(file)
        if not files:
            ctl.load("-")
        self._stats["Time"]["Load"] = timeit.default_timer() - start

        start = timeit.default_timer()
        ctl.ground()
        self._stats["Time"]["Ground Instance"] = timeit.default_timer() - start

        if self._delta is None:
            start = timeit.default_timer()
            delta = cmapf.compute_min_delta(ctl)
            self._stats["Time"]["Min Delta"] = timeit.default_timer() - start
        else:
            delta = self._delta

        parts = [("mapf", [Number(delta)])]
        if delta is None:
            res = False
        elif self._reach:
            start = timeit.default_timer()
            res = cmapf.add_reachable(ctl, delta)
            self._stats["Time"]["Reachable"] = timeit.default_timer() - start
        else:
            start = timeit.default_timer()
            res = cmapf.add_sp_length(ctl)
            self._stats["Time"]["Shortest Path"] = timeit.default_timer() - start
            parts.append(("reach", []))

        start = timeit.default_timer()
        if res:
            ctl.ground(parts)
            if self._show_reach:
                reach = ctl.symbolic_atoms.by_signature("reach", 3)
                self._stats["Reachable"] = sum(1 for _ in reach)
        else:
            # make it unsatisfiable
            with ctl.backend() as bck:
                bck.add_rule([])
        self._stats["Time"]["Ground Encoding"] = timeit.default_timer() - start

        if delta is not None:
            self._stats["Delta"] = delta

        kwargs = {"on_statistics": self._on_statistics}
        if self._costs:
            kwargs["on_model"] = self._on_model
        ctl.solve(**kwargs)


clingo_main(MAPFApp(), sys.argv[1:])
