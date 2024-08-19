import re
from watread import parse_sentences, Name, Variable
from watprefix import prefix_names, change_names
from watwrite import serialize
from repack import repack

def make_prefix(path, idx):
  if path.endswith('.wat'):
    path = path[:-4]

  # thats a guess, but should not be
  mod_name = ''.join(re.findall('[a-z]+', path))
  return f'module_{mod_name}_fn_'

class Export:
  export_name = None
  variable_name = None

  def __repr__(self):
    return f'<export {self.variable_name} as {self.export_name}>'

def merge(modules):
  all_exports = {}
  variable_remap = {}
  combined = []
  # walk to find all exports
  for mod in modules:
    name = mod[0]
    body = mod[1:]
    assert isinstance(name, Name) and name.value == 'module'
    for sentence in body:
      # print('s', sentence)
      name = sentence[0]
      assert isinstance(name, Name)
      if name.value == 'export':
        export_name = sentence[1]
        lvalue = sentence[2]
        if lvalue[0].value not in ['func', 'table']:
          continue
        assert isinstance(lvalue[1], Variable)
        export_ob = Export()
        export_ob.export_name = export_name.str_value
        export_ob.variable_name = lvalue[1].name
        all_exports[export_ob.export_name] = export_ob.variable_name

        # print('found the export', export_ob)

  # walk to find all imports and make remap table
  for mod in modules:
    name = mod[0]
    body = mod[1:]
    assert isinstance(name, Name) and name.value == 'module'
    for sentence in body:
      name = sentence[0]
      assert isinstance(name, Name)
      if name.value == 'import':
        import_mod = sentence[1].str_value
        import_fn = sentence[2].str_value
        lvalue = sentence[3]
        if lvalue[0].value not in ['func', 'table']:
          continue

        import_variable_name = lvalue[1].name
        import_str = f'{import_mod}#{import_fn}'

        export_variable_name = all_exports.get(import_str)

        if export_variable_name:
          variable_remap[import_variable_name] = export_variable_name
          # print('remap variable names from', import_variable_name, 'to', export_variable_name)

  imports = []
  head = []
  tail = []
  had_memory = False
  had_memory_export = False
  data = []
  atoms = {}
  
  total_data = 0

  data_offset = 0
  for mod in modules:
    name = mod[0]
    body = mod[1:]
    assert isinstance(name, Name) and name.value == 'module'
    found_fn = False
    data_offset += total_data
    total_data = 0
    module_data = []
    module_atoms = {}
    for sentence in body:
      name = sentence[0]
      assert isinstance(name, Name)
      if name.value == 'func':
        found_fn = True

      if name.value == 'import':
        import_mod = sentence[1].str_value
        import_fn = sentence[2].str_value
        lvalue = sentence[3]
        import_str = f'{import_mod}#{import_fn}'

        if all_exports.get(import_str):
          continue

      is_memory_export = False
      if name.value == 'export':
        lvalue = sentence[2]
        if lvalue[0].value == 'memory':
          is_memory_export = True

      if is_memory_export and had_memory_export:
        continue

      if is_memory_export:
        had_memory_export = True

      if had_memory and name.value == 'memory':
        continue

      if name.value == 'memory':
        had_memory = True
        
      if name.value == 'import':
        imports.append(sentence)
      elif name.value == 'data':
        module_data.append(sentence)
      elif name.value == 'global':
        if sentence[1].name == '__free_mem':
          total_data = int(sentence[3][1].str_value)
          sentence[3][1].str_value = str(total_data + data_offset)
          free_mem = sentence
        elif sentence[1].name.endswith('__literal_ptr_raw'):
          literal_offset = int(sentence[3][1].str_value)
          sentence[3][1].str_value = str(literal_offset + data_offset)
          data.append(sentence)
        elif sentence[1].name.endswith('__literal_ptr_e'):
          literal_offset = int(sentence[3][1].str_value) >> 2
          sentence[3][1].str_value = str(
            ((literal_offset + data_offset) << 2) | 2
          )
          data.append(sentence)
        elif sentence[1].name.startswith('__unique_atom__'):
          name = sentence[1].name
          value = int(sentence[3][1].str_value)
          module_atoms[name] = value

          if name in atoms:
            continue
          elif name not in atoms and value not in atoms.values():
            atoms[name] = value
          else:
            value = len(atoms) + 1
            atoms[name] = value
            assert value not in atoms, "Assuming the values increase monotonically"

          sentence[3][1].str_value = str(value)
          data.append(sentence)
        else:
          data.append(sentence)
      elif found_fn:
        tail.append(sentence)
      else:
        head.append(sentence)

    data += list(map(lambda d : repack(d, data_offset, atoms, module_atoms), module_data))

  if free_mem and isinstance(free_mem[2], Name):
    mut = Name()
    mut.value = 'mut'
    free_mem = free_mem[:2] + [ [mut, free_mem[2]] ] + free_mem[3:]

  combined = [ modules[0][0] ] + imports + head + [free_mem] + data + tail
  def remap_fn(item):
    remapped_name = variable_remap.get(item.name)
    remapped = Variable()
    remapped.name = remapped_name or item.name
    return remapped

  return list(change_names(remap_fn, combined))


def main(*fnames):
  modules = []
  out_fname = fnames[0]
  in_fnames = fnames[1:]
  if not in_fnames:
    return False

  for idx, fname in enumerate(in_fnames):
    with open(fname) as input_f:
      data_bytes = input_f.read()
      sentences = parse_sentences(data_bytes)
      # print('read', sentences)
      prefix = make_prefix(fname, idx)
      prefixed_s = list(prefix_names(prefix, sentences))
      modules.append(prefixed_s)
  merged_module = merge(modules)

  # print('merged', merged_module)

  out_data_bytes = serialize(merged_module)

  if out_fname == '-':
    print(out_data_bytes)
  else:
    with open(out_fname, 'w') as out_f:
      out_f.write(out_data_bytes)

  return True

if __name__ == '__main__':
  import sys
  main(*sys.argv[1:])
