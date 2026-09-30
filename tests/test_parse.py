import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from assembler import parse_line, is_number, pass1

print(is_number('five'))
print(is_number('-5'))
print(is_number('-476985.566'))
print(is_number('a15'))

#label
result = parse_line("start add 1 2 1 decrement reg1\n")
assert result == ("start", "add", "1", "2", "1"), f"failed: {result}"

#start with tab 
result = parse_line("\tlw 0 1 five\n")
assert result == (None, "lw", "0", "1", "five"), f"failed: {result}"

result = parse_line("\n")
assert result is None, f"failed: {result}"

#O-type has no field
result = parse_line("done halt\n")
assert result == ("done", "halt", None, None, None), f"failed: {result}"

#comments 
result = parse_line("start add 1 2 1 decrement reg1\n")
print(f"case comment is parsed: {result}")
assert result[2] == "1" and result[3] == "2" and result[4] == "1", "comment"

print("all parse_line tests passed")
print("-------------------")
'''
#pass1
lines_countdown = [
    "lw 0 1 five\n",
    "lw 1 2 3\n",
    "start add 1 2 1\n",
    "beq 0 1 2\n",
    "beq 0 0 start\n",
    "noop\n",
    "done halt\n",
    "five .fill 5\n",
    "neg1 .fill -1\n",
    "stAddr .fill start\n",
]
table, program = pass1(lines_countdown)
result = table
expected = {"start": 2, "done": 6, "five": 7, "neg1": 8, "stAddr": 9}
print(result)
assert result == expected, f"case 1 failed: result: {result} expected: {expected}"
'''