
import sys 

OPCODES = {
    'add': 0, 'nand': 1, 'lw': 2, 'sw': 3,
    'beq': 4, 'jalr': 5, 'halt': 6, 'noop': 7
}

R_TYPE = {'add', 'nand'}
I_TYPE = {'lw', 'sw', 'beq'}
J_TYPE = {'jalr'}
O_TYPE = {'halt', 'noop'}

#convert 16-bits 2's compliment to 32-bit signed int
def convert_num(num):
    if num & (1 << 15):
        num -= (1 << 16)
    return num

#MAX_MEM  = 65536
#NUM_REGS = 8

def error(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)