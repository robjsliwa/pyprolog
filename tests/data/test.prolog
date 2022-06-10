window(main, -2, 2.0, 20, 72).
window(error, 15, 4.0, 20, 78).
customer('John Jones', boston, good_credit).
customer('Sally Smith', chicago, good_credit).
test(Y) :- Y is 5 + 2 * 3 - 1.
test2 :- Z is 6/2, write(Z).
/*test3 :- Q is 10.*/
dog(1).
whatdog :- dog(X), write(X).
%test4(D) :- Y is 1, dog(Y).
test3(Z) :- Z is (5 + 2) * (3 - 1).
test4 :- Z is 6/2, write(Z).
c_to_f(C, F) :- F is C * 9 / 5 + 32.
c_to_fw(C) :- F is C * 9 / 5 + 32, write(F).
freezing_point(F) :- F == 32.
freezing(X) :- X =< 32.
% not_32(F) :- F =/ 32.
sum_greater_4(Y) :- X is Y + 3, X > 4.
sum_less_4 :- X is 1 + 1, X < 4.
sum_greater_eq_4 :- X is 2 + 2, X >= 4.

data(one).
data(two).
data(three).

cut_test_a(X) :-
    data(X).
cut_test_a('last clause').

test_cut(X) :-
    cut_test_a(X),
    write(X),
    nl,
    fail.

cut_test_b(X) :-
    data(X),
    !.
cut_test_b('last clause').

test_cut_b(X) :-
    cut_test_b(X),
    write(X),
    nl,
    fail.

rgb([red, green, blue]).
