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
    pass

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
    pass

class Rule:
  def __init__(self, head, tail):
    self.head = head
    self.tail = tail


# tests

known_term = Term('father_child', Term('eric'), Term('thorne'))

x = Variable('X')

goal = Term('father_child', Term('eric'), x)

bindings = goal.match(known_term)

print(f'Bindings objext is a Map: {bindings}')

value = goal.substitute(bindings)

print(f'Goal with substituted variables: {value}')
