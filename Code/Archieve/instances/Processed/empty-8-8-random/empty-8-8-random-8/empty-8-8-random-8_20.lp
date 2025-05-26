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
start(1,(1,0)).
goal(1,(1,6)).

agent(2).
start(2,(3,6)).
goal(2,(3,0)).

agent(3).
start(3,(0,7)).
goal(3,(4,7)).

agent(4).
start(4,(2,1)).
goal(4,(7,3)).

agent(5).
start(5,(2,3)).
goal(5,(1,5)).

agent(6).
start(6,(6,3)).
goal(6,(3,3)).

agent(7).
start(7,(7,4)).
goal(7,(7,1)).

agent(8).
start(8,(5,1)).
goal(8,(0,5)).

agent(9).
start(9,(3,5)).
goal(9,(6,7)).

agent(10).
start(10,(6,6)).
goal(10,(5,7)).

agent(11).
start(11,(1,3)).
goal(11,(5,5)).

agent(12).
start(12,(0,3)).
goal(12,(1,4)).

agent(13).
start(13,(6,2)).
goal(13,(5,2)).

agent(14).
start(14,(2,5)).
goal(14,(4,5)).

agent(15).
start(15,(4,3)).
goal(15,(0,1)).

agent(16).
start(16,(2,6)).
goal(16,(2,0)).

agent(17).
start(17,(4,4)).
goal(17,(6,4)).

agent(18).
start(18,(7,7)).
goal(18,(0,0)).

agent(19).
start(19,(5,3)).
goal(19,(4,6)).

agent(20).
start(20,(4,0)).
goal(20,(4,2)).

edge((X,Y),(X',Y')) :- vertex((X,Y)), vertex((X',Y')), |X-X'|+|Y-Y'|=1.
