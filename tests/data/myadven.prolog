% rooms
room(kitchen).
room(office).
room(hall).
room('dinning room').
room(cellar).

% locations
location(desk, office).
location(apple, kitchen).
location(flashlight, desk).
location('washing machine', cellar).
location(nani, 'washing machine').
location(broccoli, kitchen).
location(crackers, kitchen).
location(computer, office).

% doors
door(office, hall).
door(kitchen, office).
door(hall, 'dinning room').
door(kitchen, cellar).
door('dinning room', kitchen).

% other facts
edible(apple).
edible(crackers).

tastes_yucky(broccoli).

turned_off(flashlight).
here(kitchen).

connect(X, Y) :- door(X, Y).
connect(X, Y) :- door(Y, X).

list_things(Place) :-
    location(X, Place),
    tab,
    write(X),
    nl,
    fail.
list_things(_).

list_connections(Place) :-
    connect(Place, X),
    tab,
    write(X),
    nl,
    fail.
list_connections(_).

look :-
    here(Place),
    write('You are in the '), write(Place), nl,
    write('You can see:'), nl,
    list_things(Place),
    write('You can go to:'), nl,
    list_connections(Place).

move(Place) :-
    retract(here(_)),
    asserta(here(Place)).

goto(Place) :-
    can_go(Place),
    move(Place),
    look.

can_go(Place) :-
    here(X),
    connect(X, Place).
can_go(_) :-
    write('You cannot get there from here.'),
    nl,
    fail.

take(X) :-
    can_take(X),
    take_object(X).

can_take(Thing) :-
    here(Place),
    location(Things, Place).
can_take(Thing) :-
    write('There is no '), write(Thing),
    write(' here.'),
    nl, fail.

take_object(X) :-
    retract(location(X, _)),
    asserta(have(X)),
    write('taken'), nl.
