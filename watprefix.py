from watread import parse_sentences, Variable


def rename_prefix(prefix):
  def rename_fn(variable):
    if variable.name.startswith('module_info_'):
      return variable.prefixed(prefix)

    if variable.name.startswith('module_'):
      return variable

    if variable.name == '__free_mem':
      return variable

    if variable.name.startswith('__unique_atom__'):
      return variable

    return variable.prefixed(prefix)
  return rename_fn

def change_names(change_fn, sentences):
  for item in sentences:
    if isinstance(item, Variable):
      yield change_fn(item)
    elif isinstance(item, list):
      yield list(change_names(change_fn, item))
    else:
      yield item

def prefix_names(prefix, sentences):
  return change_names(rename_prefix(prefix), sentences)

def process(change_fn, data_bytes):
  parsed_mod = parse_sentences(data_bytes)
  return list(change_names(change_fn, parsed_mod))

def main(prefix, fname):
  with open(fname) as input_f:
    data_bytes = input_f.read()
    data = process(rename_prefix(prefix), data_bytes)

  print('read f', fname, data)

if __name__ == '__main__':
  import sys
  main(*sys.argv[1:])
