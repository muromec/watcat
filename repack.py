import struct
import array

def pad(n):
  if len(n) == 1:
    return '0' + n
  return n

def escape_bin(byte_list):
  ret = ''
  for b_value in byte_list:
    b_value_s = pad(hex(b_value)[2:])
    ret += f'\\{b_value_s}'

  return ret


def repack(data_segment, base_offset, atoms, module_atoms):
  segment_offset = int(data_segment[1][1].str_value)
  data_segment[1][1].str_value = str(segment_offset + base_offset)
  data = data_segment[2]
  str_value = data.str_value
  if not str_value or str_value[0] != '\\':
    return data_segment

  binary = b''
  for idx in range(1, len(str_value), 3):
    bt = str_value[idx:idx+2]
    binary += bytes([ int(bt, 16) ])

  binary = rebase(binary, segment_offset, base_offset, atoms, module_atoms)

  data_segment[2].str_value = escape_bin(binary)
  # assert str_value == data_segment[2].str_value

  return data_segment

def fix_value(value, segment_offset, base_offset, atoms, module_atoms):
  if (value & 0x3F) == 0xB:
    atom = value >> 6
    for key, value in module_atoms.items():
      if value == atom:
        break
    else:
      assert 'Cant find atom in the table'
    value = atoms[key]
    return (value << 6) | 0xB

  if (value & 0x3) == 2:
    raw_ptr = value >> 2
    raw_ptr += base_offset
    return (raw_ptr << 2) | 2

  return value

def rebase(binary, segment_offset, base_offset, atoms, module_atoms):
  # print('rebase', binary, segment_offset)
  offset = 0
  buffer = array.array('B', binary)
  (head, value) = struct.unpack_from('<II', buffer, offset)
  while (head & 0x3) == 1: # list pointer
    # print('offset', offset)
    raw_ptr = head >> 2
    new_ptr = raw_ptr + base_offset
    value = fix_value(value, segment_offset, base_offset, atoms, module_atoms)
    struct.pack_into('<II', buffer, offset, (new_ptr << 2) | 1, value)
    offset = raw_ptr - segment_offset
    # print('new offset', offset)
    (head, value) = struct.unpack_from('<II', buffer, offset)

  if (head & 0x3F) == 0: # tuple header
    size = head >> 6
    while size:
      offset += 4
      size -= 1
      (value, ) = struct.unpack_from('<I', buffer, offset)
      value = fix_value(value, segment_offset, base_offset, atoms, module_atoms)
      struct.pack_into('<I', buffer, offset, value)

  return bytes(buffer)

