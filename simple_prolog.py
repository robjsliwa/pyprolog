class Term:
  def __init__(self, pred, *args):
    self.pred = pred
    self.args = list(args)

  def __repr__(self):
    if len(self.args) == 0: return f'{self.pred}'
    args = ', '.join(self.args)
    return f'{self.pred}({args})'

  def __eq__(self, other):
    return self.pred == other.pred and self.args == other.args


class Rule:
  def __init__(self, head, *tail):
    self.head = head
    self.tail = list(tail)

  def __repr__(self):
    if len(self.tail) == 0: return f'{self.head}'
    preds = ', '.join(map(str, self.tail))
    return f'{self.head} :- {preds}'


def head(lst):
  return lst[:1][0]

def tail(lst):
  return lst[1:]

def append(lst1, lst2):
  return [*lst1, *lst2]

def empty(lst):
  return len(lst) == 0

def match(termA, termB):
  return termA == termB

class Interpreter:
  def __init__(self, rules):
    self.rules = rules

  def solve(self, query):
    print(f'QUERY: {query}')
    
    if not empty(query):
      for rule in self.rules:
        if match(rule.head, head(query)):
          self.solve(append(rule.tail, tail(query)))
    else:
      print('yes')
    



# a = Term('boy', 'bill')
# b = Term('mother', 'alice', 'bill')

# print(a)
# print(b)

# c = Rule(Term('mother', 'X', 'Y'), Term('mother', 'X', 'Y'), Term('boy', 'X'))

# print(c)

# d = Rule(Term('cat', 'tom'))

# print(d)

# test rules
r1 = Rule(Term('a'), Term('b'), Term('c'), Term('d'))
r2 = Rule(Term('a'), Term('e'), Term('f'))
r3 = Rule(Term('b'), Term('f'))
r4 = Rule(Term('e'))
r5 = Rule(Term('f'))
r6 = Rule(Term('a'), Term('f'))

db = [r1, r2, r3, r4, r5, r6]

i = Interpreter(db)

q = [Term('a'), Term('e')]

i.solve(q)
