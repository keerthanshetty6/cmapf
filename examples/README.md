# Approximate a SoC solution

The first example call computes reachable locations algorithmicly:
```
$ python mapf.py --delta=1 encoding.lp instances/toy1.lp
clingo version 5.6.2
Reading from encoding.lp ...
Solving...
Answer: 1
compare(a,2,2) compare(b,1,2) move(a,u,w,1) move(b,v,w,2) move(a,w,x,2)
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
$ python mapf.py --delta=1 --no-reach encoding.lp instances/toy2.lp
clingo version 5.6.2
Reading from encoding.lp ...
Solving...
Answer: 1
compare(a,2,2) compare(b,1,2) move(a,u,w,1) move(b,v,w,2) move(a,w,x,2)
Optimization: 4
OPTIMUM FOUND

Models       : 1
  Optimum    : yes
Optimization : 4
Calls        : 1
Time         : 0.003s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.003s
```
