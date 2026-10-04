import sys

NUMREGS = 8
MAXMEM = 65536
NUMMEMORY = MAXMEM   # ใช้ค่าเดียวกัน: ขนาด memory ของเครื่อง SMC

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


# ================= คนที่ 1: load_machine_code() และ main() =================

#ตั้ง state ของ pc, mem, reg, numMemory
class State:
    def __init__(self):
        self.pc = 0
        self.mem = []
        self.reg = [0] * NUMREGS
        self.num_memory = 0


#อ่านไฟล์ machine code เก็บลง mem
def load_machine_code(path):

    #สร้าง state = State()
    state = State()

    #อ่านไฟล์แล้วแยกเป็นลิสต์
    with open(path, "r") as f:
        lines = f.read().splitlines()

    #ตัดบรรทัดว่างท้ายไฟล์
    while lines and lines[-1].strip() == "":
        lines.pop()

    #บรรทัดว่างกลางไฟล์ทำให้ address เลื่อนแสดง error
    for line_no, line in enumerate(lines, start=1):
        text = line.strip()
        if text == "":
            sys.stderr.write(f"error: blank line in the middle of file (line {line_no})\n")
            sys.exit(1)
        try:
            state.mem.append(int(text))
        except ValueError:
            sys.stderr.write(f"error: line {line_no} is not an integer: {text!r}\n")
            sys.exit(1)

    #ตั้ง num_memory = len(state.mem) , ตรวจว่าไม่เกิน 65,536 คำถ้าเกินแสดง error
    state.num_memory = len(state.mem)
    if state.num_memory > MAXMEM:
        sys.stderr.write(f"error: program too large ({state.num_memory} > {MAXMEM} words)\n")
        sys.exit(1)

    #[เพิ่ม] เติม mem ด้วย 0 จนครบ 65,536 คำ เพื่อให้ lw/sw ที่อ้าง address
    # นอกช่วงโปรแกรม แต่ยังอยู่ใน 0..65535 ไม่เกิด IndexError (num_memory ยังเท่าเดิม)
    state.mem.extend([0] * (MAXMEM - state.num_memory))

    #ตั้ง reg เป็น 0 ทุกตัวและ pc = 0 แล้ว return state
    state.reg = [0] * NUMREGS
    state.pc = 0
    return state


#print state
def print_state(state):
    print("\n@@@\nstate:")
    print("\tpc", state.pc)
    print("\tmemory:")
    for i in range(state.num_memory):
        print("\t\tmem[", i, "]", state.mem[i])
    print("\tregisters:")
    for i in range(NUMREGS):
        print("\t\treg[", i, "]", state.reg[i])
    print("end state")


# ================= คนที่ 2: decoder =================

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


# ================= คนที่ 3: execute =================

def to_int32(x):  # [เพิ่ม] บีบค่ากลับเป็น 32-bit signed เหมือน int ของ C
    x &= 0xFFFFFFFF
    if x & 0x80000000:
        x -= (1 << 32)
    return x


def check_address(addr):  # [แก้: เทียบกับ NUMMEMORY (65536) ไม่ใช้ len(state.mem) และตัด param state ออก]
    if addr < 0 or addr >= NUMMEMORY:
        print(f"error: memory address {addr} out of range", file=sys.stderr)
        sys.exit(1)


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


# ================= main =================

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: python simulator_full.py <machine-code file>\n")
        sys.exit(1)
    state = load_machine_code(sys.argv[1])

    executed = 0
    while True:
        #ก่อน execute ทุก instruction
        print_state(state)
        halted = execute_instruction(state)   # [แก้] เปลี่ยนจาก step() เป็น execute_instruction()
        executed += 1
        if halted:
            break

    # ตอนจบ
    print("machine halted")
    print(f"total of {executed} instructions executed")
    print("final state of machine:")
    print_state(state)


if __name__ == "__main__":
    main()
