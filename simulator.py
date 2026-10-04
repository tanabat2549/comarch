import sys

NUMMEMORY = 65536

# opcode ตามสเปก
ADD  = 0
NAND = 1
LW   = 2
SW   = 3
BEQ  = 4
JALR = 5
HALT = 6
NOOP = 7

OPCODES = {
    ADD: "add", NAND: "nand", LW: "lw", SW: "sw",
    BEQ: "beq", JALR: "jalr", HALT: "halt", NOOP: "noop",
}


# ---- คนที่ 2: decoder ----
def convert_num(num):
    """แปลงเลข 16-bit (two's complement) เป็น signed int"""
    num &= 0xFFFF              # กันกรณีส่งค่ามากกว่า 16 bit เข้ามา
    if num & (1 << 15):        # bit 15 = 1 แปลว่าติดลบ
        num -= (1 << 16)
    return num


def decode_instruction(instr):
    """แยก field ของ instruction 32-bit แล้วคืนเป็น dict"""
    opcode   = (instr >> 22) & 0b111      # bits 24-22
    reg_a    = (instr >> 19) & 0b111      # bits 21-19
    reg_b    = (instr >> 16) & 0b111      # bits 18-16
    dest_reg = instr & 0b111              # bits 2-0  (add, nand)
    offset   = convert_num(instr & 0xFFFF)  # bits 15-0 (lw, sw, beq)

    return {
        "opcode": opcode,
        "name": OPCODES[opcode],
        "regA": reg_a,
        "regB": reg_b,
        "destReg": dest_reg,
        "offset": offset,
    }


# ---- คนที่ 3: execute ----
def to_int32(x):  # [เพิ่ม] บีบค่ากลับเป็น 32-bit signed เหมือน int ของ C
    x &= 0xFFFFFFFF
    if x & 0x80000000:
        x -= (1 << 32)
    return x


def execute_instruction(state):
    # """
    # ทำ 1 คำสั่งจาก memory[pc]
    # คืนค่า True ถ้าเป็น halt (ให้ main หยุดลูป)
    # คืนค่า False ถ้ายังไม่ halt
    # ห้ามเรียก printState ที่นี่เด็ดขาด
    # """
    check_address(state.pc)  # [เพิ่ม] กัน pc ติดลบ/เกิน (index ลบของ Python ไม่ error เอง)
    instr = state.mem[state.pc]
    d = decode_instruction(instr)  #จำลองตัวแปลงโค้ดจากกาย

    opcode  = d["opcode"]
    regA    = d["regA"]
    regB    = d["regB"]
    destReg = d["destReg"]
    offset  = d["offset"]

    if opcode == ADD:
        state.reg[destReg] = to_int32(state.reg[regA] + state.reg[regB]) #result มีค่าเป็น register 1 + register 2 [แก้: บีบเป็น 32-bit]
        state.pc += 1 #ไปบรรทัดถัดไป

    elif opcode == NAND:
        state.reg[destReg] = to_int32(~(state.reg[regA] & state.reg[regB])) #result มีค่าเป็น ค่าตรงข้ามของ register ตัวที่ 1 และ 2 ที่นำมา and กัน [แก้: บีบเป็น 32-bit]
        state.pc += 1

    elif opcode == LW:
        addr = state.reg[regA] + offset  #addr จะทำหน้าที่ในการเก็บตำแหน่งใน memory ที่คำนวณจากค่า base address ที่บวกกับค่า offset
        check_address(addr) #นำค่าที่ได้ไปเทียบกับใน memory ว่ามีจริงหรือไม่ หรือ ว่าเกินขอบเขตที่ควรจะมีหรือไม่
        state.reg[regB] = state.mem[addr] #ถ้ามีนำค่าที่ได้จาก memory[addr] ไปเก็บใน register B
        state.pc += 1

    elif opcode == SW:
        addr = state.reg[regA] + offset  #addr จะทำหน้าที่ในการเก็บตำแหน่งใน memory ที่คำนวณจากค่า base address ที่บวกกับค่า offset
        check_address(addr) #นำค่าที่ได้ไปเทียบกับใน memory ว่ามีจริงหรือไม่ หรือ ว่าเกินขอบเขตที่ควรจะมีหรือไม่
        state.mem[addr] = state.reg[regB] #นำค่าจาก register B ไปเก็บที่ตำแหน่ง addr ของ memory
        state.pc += 1

    elif opcode == BEQ:
        if state.reg[regA] == state.reg[regB]: #check register A กับ register B มีค่าเท่ากันหรือไม่
            state.pc = state.pc + 1 + offset # ถ้าเท่ากันจะทำงานที่บรรทัดตำแหน่งถัดไปบวกกับ offset
        else:
            state.pc += 1 # ถ้าไม่ก็ทำบรรทัดถัดไป

    elif opcode == JALR:
        next_pc = state.pc + 1      # เก็บไว้ก่อน เผื่อ regA == regB
        state.reg[regB] = next_pc   # เขียนลง reg[regB] ก่อน
        state.pc = state.reg[regA]  # ค่อยอ่าน reg[regA]

    elif opcode == HALT:
        state.pc += 1
        state.reg[0] = 0
        return True   #บอก main ว่าการทำงานเสร็จสิ้นแล้ว

    elif opcode == NOOP: #ไม่มี operation ข้ามการทำงานเลย
        state.pc += 1

    else: 
        print(f"error: unrecognized opcode {opcode}", file=sys.stderr)
        sys.exit(1)

    state.reg[0] = 0   # reg0 ต้องเป็น 0 เสมอ ไม่ว่าคำสั่งไหนจะพยายามเขียนทับ
    return False


def check_address(addr):  # [แก้: เทียบกับ NUMMEMORY (65536) ไม่ใช้ len(state.mem) และตัด param state ออก]
    if addr < 0 or addr >= NUMMEMORY:
        print(f"error: memory address {addr} out of range", file=sys.stderr)
        sys.exit(1)