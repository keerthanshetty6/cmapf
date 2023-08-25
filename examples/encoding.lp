% optional reachability encoding
% (that has to be grounded together with program mapf(delta).
#program reach.

% vertices that cannot be entered
block(A,V,T) :- time(A,T), horizon(B,H), goal(B,V), T >= H, A != B.

% vertices reachable from the agents start positions
forward_reach(A,U,0) :- start(A,U).
forward_reach(A,U,T) :- forward_reach(A,U,T-1), time(A,T), not block(A,U,T).
forward_reach(A,V,T) :- forward_reach(A,U,T-1), time(A,T), not block(A,V,T), edge(U,V).

% vertices reachable from the agents goal positions
reach(A,U,T) :- goal(A,U), forward_reach(A,U,T), horizon(A,T).
reach(A,U,T) :- reach(A,U,T+1), forward_reach(A,U,T).
reach(A,V,T) :- reach(A,U,T+1), forward_reach(A,V,T), edge(V,U).

% the delta value how much the length of individual agent paths can exceed their shortest path length
#program mapf(delta).

% horizon and time points
horizon(A,N+delta) :- sp_length(A,N).
horizon(M) :- M = #max { N: horizon(A,N) }.
time(A,1..N) :- horizon(A,N).
time(1..N) :- horizon(N).

% guess moves
{ move(A,U,V,T) : edge(U,V), reach(A,V,T) } 1 :- reach(A,U,T-1).

% derive locations of agents based on start positions and moves
at(A,U,0) :- start(A,U).
at(A,V,T) :- move(A,_,V,T).
at(A,U,T) :- at(A,U,T-1), not move(A,U,_,T), time(A,T).

% ensure valid moves
 :- move(A,U,_,T), not at(A,U,T-1).

% prevent invalid agent positions (due to intertia)
 :- at(A,U,T), not reach(A,U,T).

% ensure unique locations of agents
 :- { at(A,U,T) } != 1, time(A,T).

% prevent vertex conflicts
 :- { at(A,U,T) } > 1, vertex(U), time(T).

% prevent swap conflicts
 :- move(_,U,V,T), move(_,V,U,T), U < V.

% ensure that agents are at their goal positions
 :- goal(A,U), horizon(A,T), not at(A,U,T).

% compute penalties
penalty(A,N) :- sp_length(A,N+1), N >= 0.
penalty(A,T) :- sp_length(A,N), at(A,U,T), not goal(A,U), T >= N.
penalty(A,T) :- penalty(A,T+1), T >= 0.

% minimize sum of costs
#minimize { 1,A,T: penalty(A,T) }.

#show.
#show move/4.

% this is due to a glitch in clingo
#defined move/4.
#defined reach/3.
