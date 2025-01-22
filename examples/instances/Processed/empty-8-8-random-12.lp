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
start(1,(0,1)).
goal(1,(1,7)).

agent(2).
start(2,(3,1)).
goal(2,(1,0)).

agent(3).
start(3,(7,2)).
goal(3,(6,4)).

agent(4).
start(4,(1,4)).
goal(4,(0,5)).

agent(5).
start(5,(0,3)).
goal(5,(0,6)).

agent(6).
start(6,(5,5)).
goal(6,(4,0)).

agent(7).
start(7,(7,5)).
goal(7,(7,7)).

agent(8).
start(8,(3,7)).
goal(8,(5,4)).

agent(9).
start(9,(3,2)).
goal(9,(5,1)).

agent(10).
start(10,(2,2)).
goal(10,(3,5)).

agent(11).
start(11,(7,6)).
goal(11,(4,5)).

agent(12).
start(12,(0,0)).
goal(12,(5,7)).

agent(13).
start(13,(0,4)).
goal(13,(6,6)).

agent(14).
start(14,(6,7)).
goal(14,(6,5)).

agent(15).
start(15,(5,6)).
goal(15,(3,6)).

agent(16).
start(16,(1,5)).
goal(16,(2,1)).

agent(17).
start(17,(5,2)).
goal(17,(6,3)).

agent(18).
start(18,(7,3)).
goal(18,(5,3)).

agent(19).
start(19,(2,3)).
goal(19,(7,1)).

agent(20).
start(20,(7,4)).
goal(20,(5,0)).

agent(21).
start(21,(3,3)).
goal(21,(0,2)).

agent(22).
start(22,(6,0)).
goal(22,(3,4)).

agent(23).
start(23,(0,7)).
goal(23,(4,7)).

agent(24).
start(24,(1,1)).
goal(24,(2,0)).

agent(25).
start(25,(4,1)).
goal(25,(2,5)).

agent(26).
start(26,(7,0)).
goal(26,(1,3)).

agent(27).
start(27,(6,1)).
goal(27,(4,3)).

agent(28).
start(28,(4,4)).
goal(28,(1,6)).

agent(29).
start(29,(3,0)).
goal(29,(2,7)).

agent(30).
start(30,(2,6)).
goal(30,(4,6)).

agent(31).
start(31,(1,2)).
goal(31,(4,2)).

agent(32).
start(32,(6,2)).
goal(32,(2,4)).

edge((X,Y),(X',Y')) :- vertex((X,Y)), vertex((X',Y')), |X-X'|+|Y-Y'|=1.
