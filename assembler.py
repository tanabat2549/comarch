import sys
#import spec 
from spec import error, OPCODES, R_TYPE, I_TYPE, J_TYPE, O_TYPE

def is_number(text):
    try:
        int(text)
        return True
    except ValueError:
        return False

def parse_line(raw_line):
    line = raw_line.rstrip('\r\n')
    if not line.strip():  #whitespace
        return None

    label = None
    first_char = line[0]
    
    if first_char not in (' ', '\t'):
        parts = line.split(None, 1)
        label = parts[0]
        rest_line = parts[1] if len(parts) > 1 else ""
    else:
        rest_line = line.strip()

    if not rest_line:
        return label, None, None, None, None

    tokens = rest_line.split()
    opcode = tokens[0] if len(tokens) > 0 else None
    field0 = tokens[1] if len(tokens) > 1 else None
    field1 = tokens[2] if len(tokens) > 2 else None
    field2 = tokens[3] if len(tokens) > 3 else None
    return label, opcode, field0, field1, field2


#label<white>instruction<white>field0<white>field1<white>field2<white>comments
def pass1(lines):
    table = {}
    program = []
    address = 0 
    
    for i in lines:          
        parsed = parse_line(i)  
        if parsed is None:
            continue  
        label, opcode, field0, field1, field2 = parsed

        if label is not None:
            if not label[0].isalpha() or len(label) > 6:
                error(f"invalid label format: {label}")          
            if label in table:
                error(f"duplicate label in table: {label}")
            table[label] = address

        program.append((address, opcode, field0, field1, field2))  
        address = address+1

    return table, program

# pass 2 encode
def encode_r(opcode, reg_a, reg_b, dest_reg):
    return (OPCODES[opcode] << 22) | (reg_a << 19) | (reg_b << 16) | dest_reg


def encode_i(opcode, reg_a, reg_b, offset):
    # offsetField is 16-bit 2's complement, the mask keeps only the low 16 bits (-3 -> 0xFFFD)
    return (OPCODES[opcode] << 22) | (reg_a << 19) | (reg_b << 16) | (offset & 0xFFFF)


def encode_j(opcode, reg_a, reg_b):
    return (OPCODES[opcode] << 22) | (reg_a << 19) | (reg_b << 16)


def encode_o(opcode):
    return OPCODES[opcode] << 22


def parse_reg(text, address, opcode):
    if text is None:
        error(f"address {address}: missing register field for '{opcode}'")
    if not is_number(text):
        error(f"address {address}: register must be a number, got '{text}'")
    reg = int(text)
    if reg < 0 or reg > 7:
        error(f"address {address}: register out of range 0-7: {reg}")
    return reg


def resolve(text, table, address):
    # a field can be a number or a symbolic address
    if is_number(text):
        return int(text)
    if text not in table:
        error(f"address {address}: undefined label: {text}")
    return table[text]


def pass2(table, program):
    machine_code = []

    for address, opcode, field0, field1, field2 in program:
        if opcode is None:
            error(f"address {address}: label without instruction")

        if opcode == '.fill':
            if field0 is None:
                error(f"address {address}: .fill needs a value")
            value = resolve(field0, table, address)
            if value < -(1 << 31) or value > (1 << 31) - 1:
                error(f"address {address}: .fill value does not fit in 32 bits: {value}")
            machine_code.append(value)
            continue

        if opcode not in OPCODES:
            error(f"address {address}: unrecognized opcode: {opcode}")

        # parse_line always fills 3 fields, so extra words are comments;
        # each branch reads only the fields its format uses
        if opcode in R_TYPE:
            reg_a = parse_reg(field0, address, opcode)
            reg_b = parse_reg(field1, address, opcode)
            dest_reg = parse_reg(field2, address, opcode)
            machine_code.append(encode_r(opcode, reg_a, reg_b, dest_reg))

        elif opcode in I_TYPE:
            reg_a = parse_reg(field0, address, opcode)
            reg_b = parse_reg(field1, address, opcode)
            if field2 is None:
                error(f"address {address}: missing offsetField for '{opcode}'")
            offset = resolve(field2, table, address)
            # beq jumps to PC+1+offset, so a label becomes the distance from the next instruction.
            # lw/sw keep the label's address as is (used with reg 0 as the base)
            if opcode == 'beq' and not is_number(field2):
                offset = offset - (address + 1)
            if offset < -32768 or offset > 32767:
                error(f"address {address}: offsetField out of range -32768..32767: {offset}")
            machine_code.append(encode_i(opcode, reg_a, reg_b, offset))

        elif opcode in J_TYPE:
            reg_a = parse_reg(field0, address, opcode)
            reg_b = parse_reg(field1, address, opcode)
            machine_code.append(encode_j(opcode, reg_a, reg_b))

        elif opcode in O_TYPE:
            machine_code.append(encode_o(opcode))

    return machine_code


def main():
    if len(sys.argv) != 3:
        error(f"usage: {sys.argv[0]} <assembly-code file> <machine-code file>")

    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except OSError:
        error(f"can't open file {sys.argv[1]}")

    table, program = pass1(lines)
    machine_code = pass2(table, program)

    try:
        with open(sys.argv[2], 'w', newline='\n') as f:
            for word in machine_code:
                f.write(f"{word}\n")
    except OSError:
        error(f"can't write file {sys.argv[2]}")

    sys.exit(0)


if __name__ == '__main__':
    main()
