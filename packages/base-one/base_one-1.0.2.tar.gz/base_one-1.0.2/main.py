from sys import argv, stderr

def dprint(*args):
  DEBUG = False #True
  if DEBUG:
    print(*args)

def min_base1n_for_buffersize(buffer_size: int) -> int:
  """Equation from qntm readme."""
  return (256**buffer_size - 1) // (256 - 1)

def max_base1n_for_buffersize(buffer_size: int) -> int:
  """Equation from qntm readme."""
  # TODO: this - 1 is accurately placed outside of the expression, like in the readme, but this seems like a plausible place where someone could make an error, so better double-check that it's not supposed to be, effectively, inside the bottom parens.
  return (256**(buffer_size+1) - 1) / (256 - 1) - 1

def find_size_of_buffer_from_n(n: int) -> int:
  """ Given an n (the length of a base1 string),
  we must compute how long the buffer must be,
  before we fill said buffer."""
  # There's certainly a closed-form solution here that I just haven't thought about.
  # But, given that I haven't thought about it, let's do it the dumb way instead.
  i: int = 0
  while True:
    if min_base1n_for_buffersize(i) <= n <= max_base1n_for_buffersize(i):
      return i
    i+=1

def encode_l(input_buffer: bytes) -> int:
  size: int = len(input_buffer)
  dprint("size", size, type(size))
  offset: int = min_base1n_for_buffersize(size)
  dprint("offset", offset, type(offset))
  remainder: int = int.from_bytes(input_buffer, byteorder='big', signed=False)
  total: int = offset + remainder
  return total

def encode(input_buffer: bytes) -> str:
  return "A" * encode_l(input_buffer)

def decode_l(base1_string_length: int) -> bytes:
  size: int = find_size_of_buffer_from_n(base1_string_length)
  dprint("size", size, type(size))
  offset: int = min_base1n_for_buffersize(size)
  dprint("offset", offset, type(offset))
  remainder: int = base1_string_length - offset
  dprint("remainder", remainder, type(remainder))
  return remainder.to_bytes(length=size, byteorder='big', signed=False)

def decode(base1_string: str) -> bytes:
  return decode_l(len(base1_string))

def main():
  if len(argv) != 2:
    print(f"{argv[0]} must take exactly 1 argument, a string of character data to be base1 encoded.", file=stderr)
    exit(2)
  else:
    print(encode_l(argv[1].encode()))

if __name__ == "__main__":
  main()