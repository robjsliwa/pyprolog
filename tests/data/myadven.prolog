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
door(office, hall, open).
door(kitchen, office, closed).
door(hall, 'dinning room', closed).
door(kitchen, cellar, open).
door('dinning room', kitchen, closed).

% other facts
edible(apple).
edible(crackers).

tastes_yucky(broccoli).

turned_off(flashlight).

turn_on(X) :-
    turned_on(X),
    write(X), write(' is already turned on!'), nl,
    !, fail.
turn_on(X) :-
    turned_off(X),
    retract(turned_off(X)),
    assertz(turned_on(X)),
    write('You turned on '), write(X), nl, !.
turn_on(X) :-
    write('Cannot turn on '), write(X), nl,
    fail.

turn_off(X) :-
    turned_off(X),
    write(X), write(' is already turned off!'), nl,
    !, fail.
turn_off(X) :-
    turned_on(X),
    retract(turned_on(X)),
    assertz(turned_off(X)),
    write('You turned off '), write(X), nl, !.
turn_off(X) :-
    write('Cannot turn off '), write(X), nl,
    fail.

here(kitchen).

connect(X, Y, DoorState) :- door(X, Y, DoorState).
connect(X, Y, DoorState) :- door(Y, X, DoorState).

door_error(State) :-
    write('Door is already '), write(State), nl.

door_message(State, To) :-
    write('You '), write(State), write(' door to '),
    write(To), nl.

open_door(To) :-
    here(From),
    door(From, To, open),
    door_error(open),
    fail.
open_door(To) :-
    here(From),
    door(To, From, open),
    door_error(open),
    fail.
open_door(To) :-
    here(From),
    door(From, To, closed),
    retract(door(From, To, closed)),
    assertz(door(From, To, open)),
    door_message(opened, To).
open_door(To) :-
    here(From),
    door(To, From, closed),
    retract(door(To, From, closed)),
    assertz(door(To, From, open)),
    door_message(opened, To).

close_door(To) :-
    here(From),
    door(From, To, closed),
    door_error(closed),
    fail.
close_door(To) :-
    here(From),
    door(To, From, closed),
    door_error(closed),
    fail.
close_door(To) :-
    here(From),
    door(From, To, open),
    retract(door(From, To, open)),
    assertz(door(From, To, closed)),
    door_message(closed, To).
close_door(To) :-
    here(From),
    door(To, From, open),
    retract(door(To, From, open)),
    assertz(door(To, From, closed)),
    door_message(closed, To).

list_things(Place) :-
    location(X, Place),
    tab,
    write(X),
    nl,
    fail.
list_things(_).

list_connections(Place) :-
    connect(Place, X, DoorState),
    tab,
    write(X), write(' door is '), write(DoorState),
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
    connect(X, Place, open).
can_go(Place) :-
    here(X),
    connect(X, Place, closed),
    write('You cannot go there because door is closed.'),
    nl,
    !, fail.
can_go(_) :-
    write('You cannot get there from here.'),
    nl,
    fail.

take(X) :-
    can_take(X),
    take_object(X).

can_take(Thing) :-
    here(Place),
    location(Thing, Place).
can_take(Thing) :-
    write('There is no '), write(Thing),
    write(' here.'),
    nl, fail.

take_object(X) :-
    retract(location(X, _)),
    asserta(have(X)),
    write('taken'), nl.

put(Thing) :-
    have(Thing),
    here(Place),
    assertz(location(Thing, Place)),
    retract(have(Thing)),
    write('Placed '),
    write(Thing),
    write(' in '),
    write(Place),
    write('.'), nl.

list_items :-
    have(Thing),
    tab, write(Thing), nl,
    fail.
list_items.

inventory :-
    write('Your inventory: '), nl,
    list_items.
