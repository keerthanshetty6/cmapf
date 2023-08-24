import sys

from clingo.application import Application, ApplicationOptions, Flag, clingo_main
from clingo.control import Control
from clingo.symbol import Number

import cmapf


class MAPFApp(Application):
    def __init__(self):
        self._delta = 0
        self._reach = Flag(True)

    def _parse_delta(self, value: str):
        try:
            self._delta = int(value)
        except RuntimeError:
            return False

        return self._delta >= 0

    def register_options(self, options: ApplicationOptions):
        options.add("MAPF", "delta", "set the delta value [0]", self._parse_delta)
        options.add_flag(
            "MAPF", "reach", "compute reachable positions [True]", self._reach
        )

    def main(self, ctl: Control, files):
        for file in files:
            ctl.load(file)
        if not files:
            ctl.load("-")
        ctl.ground()
        parts = [("mapf", [Number(self._delta)])]
        if self._reach:
            cmapf.add_reachable(ctl, self._delta)
        else:
            cmapf.add_sp_length(ctl)
            parts.append(("reach", []))
        ctl.ground(parts)
        ctl.solve()


clingo_main(MAPFApp(), sys.argv[1:])
