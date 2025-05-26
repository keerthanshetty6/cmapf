vertex((0,0)).
vertex((0,1)).
vertex((0,2)).
vertex((0,3)).
vertex((0,4)).
vertex((0,5)).
vertex((0,6)).
vertex((0,7)).

vertex((1,0)).
vertex((1,1)).
vertex((1,2)).
vertex((1,3)).
vertex((1,4)).
vertex((1,5)).
vertex((1,6)).
vertex((1,7)).

vertex((2,0)).
vertex((2,1)).
vertex((2,2)).
vertex((2,3)).
vertex((2,4)).
vertex((2,5)).
vertex((2,6)).
vertex((2,7)).

vertex((3,0)).
vertex((3,1)).
vertex((3,2)).
vertex((3,3)).
vertex((3,4)).
vertex((3,5)).
vertex((3,6)).
vertex((3,7)).

vertex((4,0)).
vertex((4,1)).
vertex((4,2)).
vertex((4,3)).
vertex((4,4)).
vertex((4,5)).
vertex((4,6)).
vertex((4,7)).

vertex((5,0)).
vertex((5,1)).
vertex((5,2)).
vertex((5,3)).
vertex((5,4)).
vertex((5,5)).
vertex((5,6)).
vertex((5,7)).

vertex((6,0)).
vertex((6,1)).
vertex((6,2)).
vertex((6,3)).
vertex((6,4)).
vertex((6,5)).
vertex((6,6)).
vertex((6,7)).

vertex((7,0)).
vertex((7,1)).
vertex((7,2)).
vertex((7,3)).
vertex((7,4)).
vertex((7,5)).
vertex((7,6)).
vertex((7,7)).


agent(1).
start(1,(7,3)).
goal(1,(6,1)).

agent(2).
start(2,(4,1)).
goal(2,(5,6)).

agent(3).
start(3,(4,4)).
goal(3,(1,3)).

agent(4).
start(4,(5,0)).
goal(4,(7,2)).

agent(5).
start(5,(7,5)).
goal(5,(5,2)).

agent(6).
start(6,(2,5)).
goal(6,(1,6)).

agent(7).
start(7,(6,4)).
goal(7,(3,7)).

agent(8).
start(8,(1,4)).
goal(8,(1,2)).

agent(9).
start(9,(5,3)).
goal(9,(2,7)).

agent(10).
start(10,(4,7)).
goal(10,(4,2)).

agent(11).
start(11,(5,7)).
goal(11,(6,2)).

agent(12).
start(12,(2,6)).
goal(12,(5,5)).

agent(13).
start(13,(0,5)).
goal(13,(2,1)).

agent(14).
start(14,(3,2)).
goal(14,(4,0)).

agent(15).
start(15,(1,1)).
goal(15,(6,3)).

edge((X,Y),(X',Y')) :- vertex((X,Y)), vertex((X',Y')), |X-X'|+|Y-Y'|=1.
