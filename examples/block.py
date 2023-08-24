from clingo.control import Control
import cmapf

ctl = Control()

# add instance
ctl.add('''\
edge(u,w).
edge(v,w).
edge(w,x).

start(a,u).
goal(a,x).

start(b,v).
goal(b,w).
''')
ctl.ground()

# add auxiliary facts
cmapf.add_reachable(ctl, delta=0)

# add encoding here
# ...

# solve
ctl.solve(on_model=print)
