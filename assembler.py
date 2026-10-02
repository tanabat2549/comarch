import sys
#import spec 
from spec import error

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


#def 
