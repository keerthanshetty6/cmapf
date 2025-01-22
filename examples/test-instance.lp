% 5x5 grid with a wall in the middle
% a,b = start | A,B = goal
% Each agent has 3 shortest paths
% There are 4 optinal makespan/SoC solutions
%   X B
%   X X X
% a X   X A
%   X X X X
%     b
%

% optimal makespan is 6, optimal SoC is 12
% optimal solutions (same for makespan and SoC):
% at(1,(3,1),0) at(1,(3,2),1) at(1,(2,2),2) at(1,(2,3),3) at(1,(2,4),4) at(1,(3,4),5) at(1,(3,5),6)
% at(2,(1,3),0) at(2,(2,3),1) at(2,(2,4),2) at(2,(3,4),3) at(2,(4,4),4) at(2,(4,3),5) at(2,(5,3),6)

% at(1,(3,1),0) at(1,(3,2),1) at(1,(2,2),2) at(1,(2,3),3) at(1,(2,4),4) at(1,(2,5),5) at(1,(3,5),6)
% at(2,(1,3),0) at(2,(2,3),1) at(2,(2,4),2) at(2,(3,4),3) at(2,(4,4),4) at(2,(4,3),5) at(2,(5,3),6)

% at(1,(3,1),0) at(1,(3,2),1) at(1,(4,2),2) at(1,(4,3),3) at(1,(4,4),4) at(1,(3,4),5) at(1,(3,5),6)
% at(2,(1,3),0) at(2,(2,3),1) at(2,(2,2),2) at(2,(3,2),3) at(2,(4,2),4) at(2,(4,3),5) at(2,(5,3),6)

% at(1,(3,1),0) at(1,(3,2),1) at(1,(4,2),2) at(1,(4,3),3) at(1,(4,4),4) at(1,(3,4),5) at(1,(3,5),6)
% at(2,(1,3),0) at(2,(2,3),1) at(2,(2,2),2) at(2,(3,2),3) at(2,(4,2),4) at(2,(5,2),5) at(2,(5,3),6)

vertex((3,1)).

vertex((2,2)).
vertex((3,2)).
vertex((4,2)).
vertex((5,2)).

vertex((1,3)).
vertex((2,3)).
vertex((4,3)).
vertex((5,3)).

vertex((2,4)).
vertex((3,4)).
vertex((4,4)).

vertex((2,5)).
vertex((3,5)).

edge((X,Y),(X',Y')) :- vertex((X,Y)), vertex((X',Y')), |X-X'|+|Y-Y'|=1.

agent(1).
start(1,(3,1)).
goal(1,(2,3)).
%sp_length(1,4).

%agent(2).
%start(2,(1,3)).
%goal(2,(2,3)).
%sp_length(2,2).

agent(3).
start(3,(2,2)).
goal(3,(3,2)).
%sp_length(3,1).