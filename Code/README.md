### Activate Virtual environment 
```
camp/scripts/activate
```
# Approximate a SoC solution
1.Extract map to get scenario to ASP format with vertex, edges and agent start and end location - extract_map.py
2.Calculate prioirty based on Heuristics from the map extracted in step 1 - Calculate_Priority.py
3.priority.lp has ASP encoding to solve the scenario
4.MAPF_with_priority.py used to solve the mapf problem with the creation of reach variables
5.run_clingo.py finally runs all the instances


The first example call computes reachable locations algorithmicly:
```
$ python mapf.py --delta=1 encoding.lp instances/toy1.lp
clingo version 5.6.2
Reading from encoding.lp ...
Solving...
Answer: 1
cost(a,2,2) cost(b,1,2) move(a,u,w,1) move(b,v,w,2) move(a,w,x,2)
Optimization: 4
OPTIMUM FOUND

Models       : 1
  Optimum    : yes
Optimization : 4
Calls        : 1
Time         : 0.003s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.003s
```

The second example call computes reachable locations via an ASP program:
```
$ python mapf.py --delta=1 --no-reach encoding.lp instances/toy1.lp
clingo version 5.6.2
Reading from encoding.lp ...
Solving...
Answer: 1
cost(a,2,2) cost(b,1,2) move(a,u,w,1) move(b,v,w,2) move(a,w,x,2)
Optimization: 4
OPTIMUM FOUND

Models       : 1
  Optimum    : yes
Optimization : 4
Calls        : 1
Time         : 0.003s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.003s
```
