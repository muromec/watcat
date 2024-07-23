def can_be_name(byte):
  return ('a' <= byte <= 'z') or ('0' <= byte <= '9') or (byte == '.') or (byte == '_')

def can_be_name_start(byte):
  return ('a' <= byte <= 'z')

def can_be_str_literal_start(byte):
  return byte in ('"', "'")

def can_be_str_literal_end(byte):
  return byte in ('"', "'")

def can_be_num_literal_start(byte):
  return ('0' <= byte <= '9')

def can_be_num_literal(byte):
  return ('0' <= byte <= '9') or ('A' <= byte <= 'F') or ('a' <= byte <= 'f') or byte == 'x' or byte == '_'

def can_be_literal_start(byte):
  return byte in ('"', "'") or ('0' <= byte <= '9')

def can_be_literal_end(byte, literal):
  if literal.typ == 'num':
    return not can_be_num_literal(byte)
  if literal.typ == 'str':
    return byte == literal.start

  assert False

def can_be_var(byte):
  return (
    ('0' <= byte <= '9')
    or ('a' <= byte <= 'z')
    or ('A' <= byte <= 'Z')
    or byte == '_'
    or byte == '$'
    or byte == '-'
  )


class Literal:
  value = None
  str_value = None
  typ = None

  def __repr__(self):
    return f'<literal:{self.typ} {self.str_value}>'

  def to_wat(self):
    if self.typ == 'num':
      return self.str_value
    elif self.typ == 'str':
      return f'"{self.str_value}"'
    assert False, 'Invalid literal'

class Variable:
  name = None

  def __repr__(self):
    return f'<variable: ${self.name}>'

  def prefixed(self, prefix):
    copy = Variable()
    copy.name = prefix + self.name
    return copy

  def to_wat(self):
    return f'${self.name}' 

class Name:
  value = None

  def __repr__(self):
    return f'<name: {self.value}>'

  def prefixed(self, prefix):
    copy = Name()
    copy.value = prefix + self.value
    return copy

  def to_wat(self):
    return self.value

def parse_helper(data, pos, level=0):
  prev_state = None
  state = 'out'
  name = None
  literal = None
  variable = None
  children = []
  maybe_comment = None

  # print('down')
  limit = len(data)
  while pos.index < limit:
    byte = data[pos.index]

    # print('read', level, pos.index, byte, state)

    if state == 'comment' and byte in ('\n', '\r'):
      state = prev_state
    elif state == 'comment':
      pass
    elif byte == ')':
      pos.index += 1
      break
    elif state != 'comment' and maybe_comment == ';' and byte == ';':
      prev_state = state
      state = 'comment'
    elif state != 'comment' and not maybe_comment and  byte == ';':
      maybe_comment = byte
    elif state == 'out' and byte == '(':
      state = 'in'
    elif state == 'in' and not name and can_be_name_start(byte):
      state = 'name'
      name = Name()
      name.value = byte
    elif state == 'name' and can_be_name(byte):
      name.value += byte
    elif state == 'name' and name and not can_be_name(byte):
      state = 'in'
      children.append(name)
      name = None
    elif state == 'in' and byte == '(':
      child = parse_helper(data, pos, level + 1)
      children.append(child)
      continue
    elif state == 'in' and can_be_str_literal_start(byte):
      state = 'literal'
      literal = Literal()
      literal.str_value = ''
      literal.typ = 'str'
      literal.start = byte
      # print('found start of str literal')
    elif state == 'in' and can_be_num_literal_start(byte):
      state = 'literal'
      literal = Literal()
      literal.str_value = byte
      literal.typ = 'num'
    elif state == 'literal' and can_be_literal_end(byte, literal):
      state = 'in'
      children.append(literal)

      typ = literal.typ
      literal = None
      if typ == 'num':
        continue
    elif state == 'literal':
      literal.str_value += byte
    elif state == 'in' and byte == '$':
      state = 'var'
      variable = Variable()
      variable.name = ''
    elif state == 'var' and can_be_var(byte):
      variable.name += byte
    elif state == 'var' and not can_be_var(byte):
      state = 'in'
      children.append(variable)
      variable = None
      continue

    pos.index += 1

  if name:
    children.append(name)

  if literal:
    children.append(literal)

  if variable:
    children.append(variable)

  # print('up')
  return children


def parse_sentences(data):
  class Pos:
    index = 0
    
  return parse_helper(data, Pos)

def main(fname):
  with open(fname) as input_f:
    data_bytes = input_f.read()
    data = parse_sentences(data_bytes)

  # print('read f', fname, data)

if __name__ == '__main__':
  import sys
  main(*sys.argv[1:])
