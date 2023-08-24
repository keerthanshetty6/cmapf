from clingo.control import Control
import cmapf

ctl = Control()

# add instance
ctl.add('''\
edge(0,1).
edge(1,2).
edge(2,3).
edge(2,4).

start(a,0).
goal(a,3).

start(b,2).
goal(b,4).
''')
ctl.ground()

# add auxiliary facts
cmapf.add_reachable(ctl, delta=1)

# add encoding here
# ...

# solve
ctl.solve(on_model=print)
