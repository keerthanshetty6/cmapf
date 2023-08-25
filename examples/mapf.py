import sys
import timeit

from clingo.application import Application, ApplicationOptions, Flag, clingo_main
from clingo.control import Control
from clingo.symbol import Number

import cmapf


class MAPFApp(Application):
    def __init__(self):
        self._delta = None
        self._reach = Flag(True)
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
            reach = ctl.symbolic_atoms.by_signature("reach", 3)
            self._stats["Reachable"] = sum(1 for _ in reach)
        else:
            # make it unsatisfiable
            with ctl.backend() as bck:
                bck.add_rule([])
        self._stats["Time"]["Ground Encoding"] = timeit.default_timer() - start

        if delta is not None:
            self._stats["Delta"] = delta

        ctl.solve(on_statistics=self._on_statistics)


clingo_main(MAPFApp(), sys.argv[1:])
