%% setup the makespan based encoding
#program makespan(horizon).

horizon(A,horizon) :- agent(A).
horizon(horizon).

%% setup the sum of costs based encoding

#program sum_of_costs(d).

horizon(A,N+d) :- sp_length(A,N). %max per agent
horizon(M) :- M = #max { N: horizon(A,N) }.
delta(D) :- d = D.

#program mapf.
time(A,1..N) :- horizon(A,N).
time(1..N) :- horizon(N).

% Generate valid moves
{ move(A,U,V,T) : edge(U,V), reach(A,V,T) } 1 :- reach(A,U,T-1).

% Define
at(A,U,0) :- start(A,U).
at(A,V,T) :- move(A,_,V,T).
at(A,U,T) :- at(A,U,T-1), not move(A,U,_,T),reach(A,U,T).

%test
%can only move from current position
:- move(A,U,_,T), not at(A,U,T-1). 

%only one agent can occupy vertex U at time T - no 2 agent start at the same vertex (vertex conflicts)
:- {at(A,U,T)} > 1, vertex(U), time(T). 

%swap constraints
:- move(_,U,V,T), move(_,V,U,T),U!=V. 

%follow constraints
:- at(A,U,T), at(B,U,T+1), A!=B, m=fc. 

% given a time agent A can be at only one vertex it , no need to have a at for higher time T 
:- {at(A,U,T)} > 1, agent(A), time(T). 


%check
:- goal(A,U), horizon(A,T), not at(A,U,T).

%Agents stay at goal
penalty(A,N) :- sp_length(A,N+1), N >= 0.
penalty(A,T) :- sp_length(A,N), at(A,U,T), not goal(A,U), T >= N.
penalty(A,T) :- penalty(A,T+1), T >= 0.

%% the sum of costs objective
#program sum_of_costs.

bound(H+D) :- H = #sum{T,A : sp_length(A,T)}, delta(D).

:- #sum{ 1,A,T : penalty(A,T) } > B, bound(B).



%#heuristic move(A,_,V,T) : priority(A,PA), priority(B,PB), move(B,_,V,T), A != B, PA > PB. [PA,level]
%#heuristic move(A,_,V,T) : priority(A,PA), priority(B,PB), move(B,_,V,T),sp_length(A,TA),sp_length(B,TB), A != B, PA +TA > PB+TB. [PA+TA,level]
%#heuristic move(A,_,V,T) : priority(A,P) . [P,level]
%#heuristic move(A,_,V,T) : sp_length(A,TA),sp_length(B,TB), move(B,_,V,T), A != B, TA > TB. [TA,level]
% Display

#show penalty_summary/3.

#defined penalty/2.
#defined move/4.
#defined horizon/2.
#defined sp_length/2.
#defined bound/1.
#defined penalty_summary/3.
#defined reach/3.

priority(10,99).
priority(15,99).
priority(20,99).
priority(24,99).
priority(27,99).
priority(31,99).
priority(6,98).
priority(19,98).
priority(25,98).
priority(12,97).
priority(14,97).
priority(17,97).
priority(26,97).
priority(29,97).
priority(30,97).
priority(11,96).
priority(16,96).
priority(21,96).
priority(2,95).
priority(3,95).
priority(4,95).
priority(32,95).
priority(7,94).
priority(5,93).
priority(9,93).
priority(22,92).
priority(1,91).
priority(13,90).
priority(18,90).
priority(8,89).
priority(23,89).
priority(28,88).