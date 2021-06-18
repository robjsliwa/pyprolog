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
door('dinninr room', kitchen).

% other facts
edible(apple).
edible(crackers).

tastes_yucky(broccoli).

turned_off(flashlight).
here(kitchen).
