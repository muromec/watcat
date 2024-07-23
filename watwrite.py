from watread import Name

def serialize(sentences, ident=0):
  p = ' '*ident
  # print('s', ident, sentences,)
  if not sentences:
    return ''
  ret = ''
  head = sentences[0]
  assert isinstance(head, Name)
  ret += f'\n{p}({head.value}'
  ident += 2
  p = ' '*ident
  for item in sentences[1:]:
    if isinstance(item, list):
      ret += serialize(item, ident + 2)
    else:
      ret += p + item.to_wat() + ' '

  ident -= 2
  p = ' '*ident
  ret += f'\n{p})'
  return ret
