import sys
#import spec 
from spec import error, OPCODES, R_TYPE, I_TYPE, J_TYPE, O_TYPE

def is_number(text): # method ตรวจสอบว่า text สามารถแปลงเป็นจำนวนเต็มได้ไหม 
    try:  
        int(text)
        return True
    except ValueError:
        return False
    
# method แยก line ของ code assembly ออกเป็น label, opcode, field0, field1, field2
def parse_line(raw_line):
    line = raw_line.rstrip('\r\n') #ตัด \r\n ออกจากท้าย line
    if not line.strip():  #whitespace case
        return None

    label = None 
    first_char = line[0]  
    
    if first_char not in (' ', '\t'): # ถ้า first_char ไม่ใช่ whitespace แสดงว่า line นี้มี label
        parts = line.split(None, 1) # split line ออกเป็น 2 ส่วน โดยใช้ whitespace เป็นตัวแบ่งทั้งสองส่วนออกจากกัน
        label = parts[0] #โดย label จะเป็นส่วนแรกของ line และที่เหลือของ line จะเป็น rest_line
        rest_line = parts[1] if len(parts) > 1 else "" #เงื่อนไขนี้ตรวจสอบว่า หลังแยก label ออก ยังมีส่วนที่เหลือมั้ย ถ้ามีให้ rest_line เป็นส่วนเหลือ ถ้าไม่มีให้ rest_line เป็น string ว่าง กัน index error
    else:
        rest_line = line.strip() #ตัด whitespace ออกจากทั้งสองด้านของ line

    if not rest_line: #เงื่อนไขนี้ตรวจสอบว่า rest_line เป็นstrว่าง? ถ้าว่าง แสดงว่า line นี้มี label แต่ไม่มี instruction ให้ return label และ None
        return label, None, None, None, None # none 4 ตัวนี้แทนค่า opcode, field0, field1, field2 เพื่อให้ pass1() สามารถตรวจสอบได้ว่ามี label แต่ไม่มี instruction

    tokens = rest_line.split()
    opcode = tokens[0] if len(tokens) > 0 else None #หา opcode จาก tokens ถ้า tokens มีความยาวมากกว่า 0 ให้ opcode เป็น token แรก ถ้าไม่ เป็น None
    field0 = tokens[1] if len(tokens) > 1 else None #ถ้า tokens มีความยาวมากกว่า 1 ให้ field0 เป็น token ที่สอง ถ้าไม่ เป็น None
    field1 = tokens[2] if len(tokens) > 2 else None 
    field2 = tokens[3] if len(tokens) > 3 else None 
    return label, opcode, field0, field1, field2 

#label<white>instruction<white>field0<white>field1<white>field2<white>comments
def pass1(lines): #สร้าง symbol table และแยก instruction ออกเป็น opcode และ fields
    table = {}
    program = []
    address = 0 
    # loop ทุกบรรทัดในไฟล์
    for i in lines:          
        parsed = parse_line(i)  
        if parsed is None: #ถ้า parsed เป็น None หมายความว่า line เป็น whitespace ให้ข้ามไปบรรทัดถัดไปโดยไม่เพิ่ม address
            continue  
        label, opcode, field0, field1, field2 = parsed

        if label is not None: #ตรวจสอบ label ว่าถูกต้องตาม format ไหม
            if not label[0].isalpha() or not label.isalnum() or len(label) > 6: #เช็คว่า label เริ่มต้นด้วยตัวอักษร ใน labelต้องเป็นแค่ตัวอักษรและตัวเลข และยาวไม่เกิน 6 ตัว ถ้าไม่ ถือว่า error
                error(f"invalid label format: {label}")          
            if label in table: #if duplicate
                error(f"duplicate label in table: {label}")
            table[label] = address #เพิ่ม label และ address ลงใน symbol table

        program.append((address, opcode, field0, field1, field2))  #เพิ่ม instruction ลงใน program list
        address = address+1 #เพิ่ม address สำหรับ instruction ถัดไป

    return table, program

# pass 2 encode
def encode_r(opcode, reg_a, reg_b, dest_reg): # left shift to the right bit position following R-type format and combine the fields
    return (OPCODES[opcode] << 22) | (reg_a << 19) | (reg_b << 16) | dest_reg

# left shift to the right bit position following I-type format and combine the fields
def encode_i(opcode, reg_a, reg_b, offset):
    # offsetField is 16-bit 2's complement
    return (OPCODES[opcode] << 22) | (reg_a << 19) | (reg_b << 16) | (offset & 0xFFFF) # offset & 0xFFFF keeps the lower 16 bits of the offset

# left shift to the right bit position following J-type format and combine the fields
def encode_j(opcode, reg_a, reg_b):
    return (OPCODES[opcode] << 22) | (reg_a << 19) | (reg_b << 16)

# left shift to the right bit position following O-type format
def encode_o(opcode):
    return OPCODES[opcode] << 22


def parse_reg(text, address, opcode): # find the register number from the text
    if text is None: # if the text is None, it means the register field is missing
        error(f"address {address}: missing register field for '{opcode}'")
    if not is_number(text): # if the text is not a number, it means the register field is invalid
        error(f"address {address}: register must be a number, got '{text}'")
    reg = int(text) # convert the text to an integer
    if reg < 0 or reg > 7: # check if the register number is in range 0-7
        error(f"address {address}: register out of range 0-7: {reg}")
    return reg


def resolve(text, table, address): # resolve the text to a number or a symbolic address
    # a field can be a number or a symbolic address
    if is_number(text): # if the text is a number, return the integer value of the text
        return int(text)
    if text not in table: # if the text is not in the table, it means the label is undefined
        error(f"address {address}: undefined label: {text}")
    return table[text] # if the text is in the table, return the address of the label

# convert the program to machine code
def pass2(table, program):
    machine_code = []
    # loop each line of the program
    for address, opcode, field0, field1, field2 in program:
        if opcode is None: # if the opcode is None, it means the line is a label without an instruction
            error(f"address {address}: label without instruction")

        if opcode == '.fill': # if the opcode is .fill, it means the line is a number or a symbolic address
            if field0 is None: # missing value for .fill
                error(f"address {address}: .fill needs a value")
            value = resolve(field0, table, address) # resolve the value to a number or a symbolic address
            if value < -(1 << 31) or value > (1 << 31) - 1: # check if the value fits in 32 bits
                error(f"address {address}: .fill value does not fit in 32 bits: {value}")
            machine_code.append(value) # append the value to the machine code
            continue # skip the rest of the loop for .fill

        if opcode not in OPCODES: # check if the opcode is invalid
            error(f"address {address}: unrecognized opcode: {opcode}")

        
        # parse the fields and encode the instruction based on the opcode type
        if opcode in R_TYPE:
            reg_a = parse_reg(field0, address, opcode)
            reg_b = parse_reg(field1, address, opcode)
            dest_reg = parse_reg(field2, address, opcode)
            machine_code.append(encode_r(opcode, reg_a, reg_b, dest_reg))

        elif opcode in I_TYPE: # parse the fields and encode the instruction based on the opcode type
            reg_a = parse_reg(field0, address, opcode)
            reg_b = parse_reg(field1, address, opcode)
            if field2 is None: # if the field2 is None, it means the offsetField is missing
                error(f"address {address}: missing offsetField for '{opcode}'")
            offset = resolve(field2, table, address) # resolve the offsetField to a number or a symbolic address
            # lw/sw keep the label address
            # if beq and the offsetField is a label, calculate the offset
            if opcode == 'beq' and not is_number(field2):
                offset = offset - (address + 1) # target = (PC + 1) + offset, offset = target - (PC + 1)
            if offset < -32768 or offset > 32767: # check if the offsetField fits in 16 bits signed
                error(f"address {address}: offsetField out of range -32768..32767: {offset}")
            machine_code.append(encode_i(opcode, reg_a, reg_b, offset)) # append the encoded instruction to the machine code

        elif opcode in J_TYPE: # parse the fields and encode the instruction based on the opcode type
            reg_a = parse_reg(field0, address, opcode)
            reg_b = parse_reg(field1, address, opcode)
            machine_code.append(encode_j(opcode, reg_a, reg_b))

        elif opcode in O_TYPE: # parse the fields and encode the instruction based on the opcode type
            machine_code.append(encode_o(opcode))

    return machine_code


def main():
    if len(sys.argv) != 3: # check argument, this file, input file, output file 
        error(f"usage: {sys.argv[0]} <assembly-code file> <machine-code file>")

    try: # read each line of the input file
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except OSError:
        error(f"can't open file {sys.argv[1]}")

    table, program = pass1(lines) # perform the first pass to build the symbol table and parse the program
    machine_code = pass2(table, program) # perform the second pass to encode the program into machine code

    try: # write each line of the machine code to the output file
        with open(sys.argv[2], 'w', newline='\n') as f:
            for word in machine_code: # write each word of the machine code to the output file
                f.write(f"{word}\n")
    except OSError:
        error(f"can't write file {sys.argv[2]}")

    sys.exit(0)


if __name__ == '__main__':
    main()
