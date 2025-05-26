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
start(1,(3,0)).
goal(1,(5,2)).

agent(2).
start(2,(4,3)).
goal(2,(5,4)).

agent(3).
start(3,(6,2)).
goal(3,(0,6)).

agent(4).
start(4,(7,1)).
goal(4,(0,1)).

agent(5).
start(5,(3,1)).
goal(5,(6,0)).

agent(6).
start(6,(2,1)).
goal(6,(3,2)).

agent(7).
start(7,(7,5)).
goal(7,(3,6)).

agent(8).
start(8,(2,4)).
goal(8,(6,3)).

agent(9).
start(9,(3,5)).
goal(9,(1,6)).

agent(10).
start(10,(4,4)).
goal(10,(6,5)).

agent(11).
start(11,(4,1)).
goal(11,(3,3)).

agent(12).
start(12,(5,6)).
goal(12,(1,7)).

agent(13).
start(13,(5,0)).
goal(13,(4,5)).

agent(14).
start(14,(5,7)).
goal(14,(7,6)).

agent(15).
start(15,(6,7)).
goal(15,(0,4)).

agent(16).
start(16,(1,3)).
goal(16,(0,5)).

agent(17).
start(17,(0,2)).
goal(17,(7,0)).

agent(18).
start(18,(4,2)).
goal(18,(2,2)).

agent(19).
start(19,(5,5)).
goal(19,(0,3)).

agent(20).
start(20,(7,2)).
goal(20,(5,1)).

agent(21).
start(21,(0,0)).
goal(21,(3,4)).

agent(22).
start(22,(6,1)).
goal(22,(3,7)).

agent(23).
start(23,(7,7)).
goal(23,(2,6)).

agent(24).
start(24,(7,3)).
goal(24,(2,3)).

agent(25).
start(25,(2,7)).
goal(25,(1,2)).

agent(26).
start(26,(1,0)).
goal(26,(1,1)).

agent(27).
start(27,(2,5)).
goal(27,(2,0)).

agent(28).
start(28,(5,3)).
goal(28,(6,6)).

agent(29).
start(29,(4,7)).
goal(29,(0,7)).

agent(30).
start(30,(7,4)).
goal(30,(4,6)).

agent(31).
start(31,(1,4)).
goal(31,(1,5)).

agent(32).
start(32,(6,4)).
goal(32,(4,0)).

edge((X,Y),(X',Y')) :- vertex((X,Y)), vertex((X',Y')), |X-X'|+|Y-Y'|=1.
