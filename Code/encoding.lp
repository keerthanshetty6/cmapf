%%% setup

%% setup the makespan based encoding
#program makespan(horizon).

horizon(A,horizon) :- agent(A).
horizon(horizon).

%% setup the sum of costs based encoding
#program sum_of_costs(delta).

horizon(A,N+delta) :- sp_length(A,N).
horizon(M) :- M = #max { N: horizon(A,N) }.

delta(D) :- delta = D.
%%% the basic mapf encoding

#program mapf.

time(A,1..N) :- horizon(A,N).
time(1..N) :- horizon(N).

%% optional reachability encoding (part of program mapf)
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

%% continue mapf program
#program mapf.

% guess moves
{ move(A,U,V,T) : edge(U,V), reach(A,V,T) } 1 :- reach(A,U,T-1).

% derive locations of agents based on start positions and moves
at(A,U,0) :- start(A,U).
at(A,V,T) :- move(A,_,V,T).
at(A,U,T) :- at(A,U,T-1), not move(A,U,_,T), reach(A,U,T).

% ensure valid moves
 :- move(A,U,_,T), not at(A,U,T-1).

% ensure unique locations of agents
 :- { at(A,U,T) } != 1, time(A,T).

% prevent vertex conflicts
 :- { at(A,U,T) } > 1, vertex(U), time(T).

% prevent swap conflicts
 :- move(_,U,V,T), move(_,V,U,T), U < V.

% ensure that agents are at their goal positions
 :- goal(A,U), horizon(A,T), not at(A,U,T).

%%% objectives

% compute penalties
% - for the makespan objective it might be better to project out
%   the agent right away to have just one chain
% - predicate penalty/2 is currently used by the mapf solver
%   for both objectives
penalty(A,N) :- sp_length(A,N+1), N >= 0.
penalty(A,T) :- sp_length(A,N), at(A,U,T), not goal(A,U), T >= N.
penalty(A,T) :- penalty(A,T+1), T >= 0.

%% the sum of costs objective
#program sum_of_costs.

% minimize some of costs
bound(H+D) :- H = #sum{T,A : sp_length(A,T)}, delta(D).

:- #sum{ 1,A,T : penalty(A,T) } > B, bound(B).



%% the makespan objective
#program makespan.

% minimize makespan
#minimize { 1,T: penalty(_,T) }.

%%% meta statements

#show.


% prevent warnings from clingo
#defined penalty/2.
#defined move/4.
#defined reach/3.