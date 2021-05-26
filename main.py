import re
from functools import reduce


class Variable:
  def __init__(self, name):
    self.name = name

  def match(self, other):
    bindings = dict()
    if self != other:
      bindings[self] = other
    return bindings

  def substitute(self, bindings):
    value = bindings.get(self, None)
    if value is not None:
      return value.substitute(bindings)
    return self

  def __str__(self):
    return str(self.name)
  
  def __repr__(self):
    return str(self)


def merge_bindings(bindings1, bindings2):
  if bindings1 is None or bindings2 is None:
    return None

  bindings = dict()

  bindings = { **bindings1 }

  for variable, value in bindings2.items():
    if variable in bindings:
      other = bindings[variable]
      sub  = other.match(value)

      if sub is not None:
        for var, val in sub.items():
          bindings[var] = val
      else:
        return None
    else:
      bindings[variable] = value
  
  return bindings

class Term:
  def __init__(self, pred, *args):
    self.pred = pred
    self.args = list(args)
  
  def match(self, other):
    if isinstance(other, Term):
      if self.pred != other.pred or \
        len(self.args) != len(other.args):
        return None

      m = list(
            map(
              (lambda arg1, arg2: arg1.match(arg2)),
              self.args,
              other.args
            )
      )

      return reduce(merge_bindings, [{}] + m)

    return other.match(self)
  
  def substitute(self, bindings):
    return Term(self.pred, *map(
      (lambda arg: arg.substitute(bindings)),
      self.args
    ))

  def query(self, db):
    yield from db.query(self)

  def __str__(self):
    if len(self.args) == 0: return f'{self.pred}'
    args = ', '.join(map(str, self.args))
    return f'{self.pred}({args})'

  def __repr__(self):
    return str(self)

class TRUE(Term):
  def __init__(self):
    super().__init__(TRUE)

  def substitute(self, bindings):
    return self

  def query(self, db):
    yield self

class Rule:
  def __init__(self, head, body):
    self.head = head
    self.body = body


class Conjunction(Term):
  def __init__(self, args):
    super().__init__(None, *args)

  def query(self, db):
    def solutions(index, bindings):
      if index >= len(self.args):
        yield self.substitute(bindings)
      else:
        arg = self.args[index]
        for item in db.query(arg.substitute(bindings)):
          unified = merge_bindings(
            arg.match(item),
            bindings
          )
          if unified is not None:
            yield from solutions(index + 1, unified)
    
    yield from solutions(0, {})

  def substitute(self, bindings):
    return Conjunction(
      map(
        (lambda arg: arg.substitute(bindings)),
        self.args
      )
    )


class Database:
  def __init__(self, rules):
    self.rules = rules

  def query(self, goal):
    for rule in self.rules:
      match = rule.head.match(goal)
      if match is not None:
        head = rule.head.substitute(match)
        body = rule.body.substitute(match)
        # print(f'body: {body}')
        for item in body.query(self):
          yield head.substitute(body.match(item))


# Parser

TOKEN_REGEX = r"[A-Za-z0-9_]+|:\-|[()\.,]"
ATOM_NAME_REGEX = r"^[A-Za-z0-9_]+$"
VARIABLE_REGEX = r"^[A-Z_][A-Za-z0-9_]*$"

def lexer(text):
  matches = re.findall(TOKEN_REGEX, text)

  for token in matches:
    yield token


def parser(tokens):
  current = ''
  is_done = False
  scope = {}

  def advance():
    try:
      next_token = next(tokens)
      nonlocal current
      current = next_token
      nonlocal is_done
    except StopIteration:
      is_done = True
    
  def parse_atom():
    name = current
    if re.match(ATOM_NAME_REGEX, name) is None:
      raise Exception(f'Bad atom name: {name}')
      
    advance()
    return name
    
  def parse_term():
    if current == '(':
      advance()
      args = []
      while current != ')':
        args.append(parse_term())
        if current != ',' and current != ')':
          raise Exception(f'Expecter , or ) in term but got {current}')
        if current == ',':
          advance()
      
      advance()
      return Conjunction(args)
    
    predicate = parse_atom()
    if re.match(VARIABLE_REGEX, predicate) is not None:
      if predicate == '_':
        return Variable('_')
      
      variable = scope.get(predicate, None)
      if variable is None:
        variable = Variable(predicate)
        scope[predicate] = variable
      return variable
      
    if current != '(':
      return Term(predicate)
      
    advance()
    args = []
    while current != ')':
      args.append(parse_term())
      if current != ',' and current != ')':
        raise Exception(f'Expected , or ) in term but got {current}')
      
      if current == ',':
        advance()
    
    advance()
    return Term(predicate, *args)
    
  def parse_rule():
    head = parse_term()
    
    if current == '.':
      advance()
      return Rule(head, TRUE())
      
    if current != ':-':
      raise Exception(f'Expected :- in rule but got {current}')
      
    advance()
    args = []
    while current != '.':
      args.append(parse_term())
      if current != ',' and current != '.':
        raise Exception(f'Expected , or ) in term but got {current}')
        
      if current == ',':
        advance()
        
    
    advance()
    body = None
    if len(args) == 1:
      body = args[0]
    else:
      body = Conjunction(args)
      
    return Rule(head, body)
    
  def parse_rules():
    rules = []
    while not is_done:
      nonlocal scope
      scope = {}
      rules.append(parse_rule())
    return rules
    
  def term_parser():
    nonlocal scope
    scope = {}
    return parse_term()
    
  advance()
  return {
    'parse_rules': parse_rules,
    'parse_term': term_parser
  }
  


# tests

known_term = Term('father_child', Term('eric'), Term('thorne'))

x = Variable('X')

goal = Term('father_child', Term('eric'), x)

bindings = goal.match(known_term)

print(f'Bindings objext is a Map: {bindings}')

value = goal.substitute(bindings)

print(f'Goal with substituted variables: {value}')

sample_prolog = '''
father_child(massimo, ridge).
father_child(eric, thorne).
father_child(thorne, alexandria).

mother_child(stephanie, thorne).
mother_child(stephanie, kristen).
mother_child(stephanie, felicia).

parent_child(X, Y) :- father_child(X, Y).
parent_child(X, Y) :- mother_child(X, Y).

sibling(X, Y) :- parent_child(Z, X), parent_child(Z, Y).
'''

rules = parser(lexer(sample_prolog))['parse_rules']()

db = Database(rules)

goal_text = 'sibling(X, kristen)'

goal = parser(lexer(goal_text))['parse_term']()

x = goal.args[0]

for item in db.query(goal):
  print(item)
  print(f'value of X = {goal.match(item).get(x)}')

for token in lexer('mother_child(X, kristen)'):
  print(token)
  

# parser tests

rules_text = '''
mother_child(stephanie, thorne).
mother_child(stephanie, kristen).
mother_child(stephanie, felicia).
'''

rules = parser(lexer(rules_text))['parse_rules']()

db = Database(rules)

goal_text = 'mother_child(X, kristen)'

goal = parser(lexer(goal_text))['parse_term']()

x = goal.args[0]

for item in db.query(goal):
  print(item)
  print(f'value of X = {goal.match(item).get(x)}')


# Einstein's puzzle

print('Puzzle 1...')

puzzle = '''
exists(A, list(A, _, _, _, _)).
exists(A, list(_, A, _, _, _)).
exists(A, list(_, _, A, _, _)).
exists(A, list(_, _, _, A, _)).
exists(A, list(_, _, _, _, A)).

rightOf(R, L, list(L, R, _, _, _)).
rightOf(R, L, list(_, L, R, _, _)).
rightOf(R, L, list(_, _, L, R, _)).
rightOf(R, L, list(_, _, _, L, R)).

middle(A, list(_, _, A, _, _)).

first(A, list(A, _, _, _, _)).

nextTo(A, B, list(B, A, _, _, _)).
nextTo(A, B, list(_, B, A, _, _)).
nextTo(A, B, list(_, _, B, A, _)).
nextTo(A, B, list(_, _, _, B, A)).
nextTo(A, B, list(A, B, _, _, _)).
nextTo(A, B, list(_, A, B, _, _)).
nextTo(A, B, list(_, _, A, B, _)).
nextTo(A, B, list(_, _, _, A, B)).

puzzle(Houses) :-
    exists(house(red, english, _, _, _), Houses),
    exists(house(_, spaniard, _, _, dog), Houses),
    exists(house(green, _, coffee, _, _), Houses),
    exists(house(_, ukrainian, tea, _, _), Houses),
    rightOf(house(green, _, _, _, _), house(ivory, _, _, _, _), Houses),
    exists(house(_, _, _, oldgold, snails), Houses),
    exists(house(yellow, _, _, kools, _), Houses),
    middle(house(_, _, milk, _, _), Houses),
    first(house(_, norwegian, _, _, _), Houses),
    nextTo(house(_, _, _, chesterfield, _), house(_, _, _, _, fox), Houses),
    nextTo(house(_, _, _, kools, _),house(_, _, _, _, horse), Houses),
    exists(house(_, _, orangejuice, luckystike, _), Houses),
    exists(house(_, japanese, _, parliament, _), Houses),
    nextTo(house(_, norwegian, _, _, _), house(blue, _, _, _, _), Houses),
    exists(house(_, _, water, _, _), Houses),
    exists(house(_, _, _, _, zebra), Houses).

solution(WaterDrinker, ZebraOwner) :-
    puzzle(Houses),
    exists(house(_, WaterDrinker, water, _, _), Houses),
    exists(house(_, ZebraOwner, _, _, zebra), Houses).
'''

rules = parser(lexer(puzzle))['parse_rules']()

db = Database(rules)

goal_text = 'solution(WaterDrinker, ZebraOwner)'

goal = parser(lexer(goal_text))['parse_term']()

x = goal.args[0]

for item in db.query(goal):
  print(item)
  print(f'value of X = {goal.match(item).get(x)}')

print('Puzzle 2...')

puzzle = '''
exists(A, list(A, _, _, _, _)).
exists(A, list(_, A, _, _, _)).
exists(A, list(_, _, A, _, _)).
exists(A, list(_, _, _, A, _)).
exists(A, list(_, _, _, _, A)).

rightOf(R, L, list(L, R, _, _, _)).
rightOf(R, L, list(_, L, R, _, _)).
rightOf(R, L, list(_, _, L, R, _)).
rightOf(R, L, list(_, _, _, L, R)).

middle(A, list(_, _, A, _, _)).

first(A, list(A, _, _, _, _)).

nextTo(A, B, list(B, A, _, _, _)).
nextTo(A, B, list(_, B, A, _, _)).
nextTo(A, B, list(_, _, B, A, _)).
nextTo(A, B, list(_, _, _, B, A)).
nextTo(A, B, list(A, B, _, _, _)).
nextTo(A, B, list(_, A, B, _, _)).
nextTo(A, B, list(_, _, A, B, _)).
nextTo(A, B, list(_, _, _, A, B)).

puzzle(Houses) :-
  exists(house(red, british, _, _, _), Houses),
  exists(house(_, swedish, _, _, dog), Houses),
  exists(house(green, _, coffee, _, _), Houses),
  exists(house(_, danish, tea, _, _), Houses),
  rightOf(house(white, _, _, _, _), house(green, _, _, _, _), Houses),
  exists(house(_, _, _, pall_mall, bird), Houses),
  exists(house(yellow, _, _, dunhill, _), Houses),
  middle(house(_, _, milk, _, _), Houses),
  first(house(_, norwegian, _, _, _), Houses),
  nextTo(house(_, _, _, blend, _), house(_, _, _, _, cat), Houses),
  nextTo(house(_, _, _, dunhill, _),house(_, _, _, _, horse), Houses),
  exists(house(_, _, beer, bluemaster, _), Houses),
  exists(house(_, german, _, prince, _), Houses),
  nextTo(house(_, norwegian, _, _, _), house(blue, _, _, _, _), Houses),
  nextTo(house(_, _, _, blend, _), house(_, _, water_, _, _), Houses).

solution(FishOwner) :-
  puzzle(Houses),
  exists(house(_, FishOwner, _, _, fish), Houses).
'''

rules = parser(lexer(puzzle))['parse_rules']()

db = Database(rules)

goal_text = 'solution(FishOwner)'

goal = parser(lexer(goal_text))['parse_term']()

x = goal.args[0]

for item in db.query(goal):
  print(item)
  print(f'value of X = {goal.match(item).get(x)}')