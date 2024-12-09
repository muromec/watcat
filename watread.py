from parse_wat import Lark_StandAlone, Transformer


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

parser = Lark_StandAlone()

class WatTransformer(Transformer):
  def module(self, items):
    return items[0]

  def UCASE_LETTER(self, items):
    return items[0]

  def LCASE_LETTER(self, items):
    return items[0]

  def DIGIT(self, items):
    (d,) = items
    return d

  def HEX_DIGIT(self, items):
    (d,) = items
    return d

  def UNDER(self, items):
    return '_'

  def dec_number(self, items):
    return int("".join(items), 10)

  def hex_number(self, items):
    return int("".join(items), 16)

  def MINUS(self, items):
    return -1

  def number(self, items):
    if len(items) == 1:
      (n,) = items
    elif len(items) == 2:
      (sign, n) = items
      n = n * sign
    else:
      assert False

    literal = Literal()
    literal.typ = 'num'
    literal.str_value = str(n)
    return literal

  def name(self, items):
    ret = Name()
    ret.value = "".join(items)
    return ret

  def var_name(self, items):
    ret = Variable()
    ret.name = "".join(items)
    return ret

  def variable(self, items):
    (v,) = items
    return v

  def ARG_SPACE(self, items):
    return None

  def ESCAPED_STRING(self, items):
    return items[1:-1]

  def string(self, items):
   (v,) = items
   literal = Literal()
   literal.typ = 'str'
   literal.str_value = v
   return literal

  def statement(self, items):
    ret = list([
     part
     for part in items
     if part is not None
    ])
    return ret

  def value(self, items):
    (v,) = items
    return v

def parse_sentences(data):
  transformer = WatTransformer()
  return transformer.transform(
    parser.parse(data)
  )

def main(fname):
  with open(fname) as input_f:
    data_bytes = input_f.read()
    data = parse_sentences(data_bytes)

  print('read f', fname, data)

if __name__ == '__main__':
  import sys
  main(*sys.argv[1:])
