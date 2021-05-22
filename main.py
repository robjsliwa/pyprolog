class Term:
  def __init__(self, pred, *args):
    self._pred = pred
    self._args = args

  def __repr__(self):
    args = ', '.join(self._args)
    return f'{self._pred}({args})'


class Rule:
  def __init__(self, rule, *args):
    self._rule = rule
    self._args = args
    self._terms = []

  def add_term(self, term):
    self._terms.append(term)
    return self

  def __repr__(self):
    rule_args = ', '.join(self._args)
    preds = ', '.join(map(str, self._terms))
    return f'{self._rule}({rule_args}) :- {preds}'


a = Term('boy', 'bill')
b = Term('mother', 'alice', 'bill')

print(a)
print(b)

c = Rule('son', 'X', 'Y')
c.add_term(Term('mother', 'X', 'Y')).add_term(Term('boy', 'X'))

print(c)

