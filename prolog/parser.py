import re
from .interpreter import Conjunction, Variable, Term, Rule, TRUE


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