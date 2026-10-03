import sys

# opcode ตามสเปก
ADD  = 0
NAND = 1
LW   = 2
SW   = 3
BEQ  = 4
JALR = 5
HALT = 6
NOOP = 7


def execute_instruction(state):
    # """
    # ทำ 1 คำสั่งจาก memory[pc]
    # คืนค่า True ถ้าเป็น halt (ให้ main หยุดลูป)
    # คืนค่า False ถ้ายังไม่ halt
    # ห้ามเรียก printState ที่นี่เด็ดขาด
    # """
    instr = state.mem[state.pc]
    d = decode_instruction(instr)  #จำลองตัวแปลงโค้ดจากกาย

    opcode  = d["opcode"]
    regA    = d["regA"]
    regB    = d["regB"]
    destReg = d["destReg"]
    offset  = d["offset"]

    if opcode == ADD:
        state.reg[destReg] = state.reg[regA] + state.reg[regB] #result มีค่าเป็น register 1 + register 2
        state.pc += 1 #ไปบรรทัดถัดไป

    elif opcode == NAND:
        state.reg[destReg] = ~(state.reg[regA] & state.reg[regB]) #result มีค่าเป็น ค่าตรงข้ามของ register ตัวที่ 1 และ 2 ที่นำมา and กัน
        state.pc += 1

    elif opcode == LW:
        addr = state.reg[regA] + offset  #addr จะทำหน้าที่ในการเก็บตำแหน่งใน memory ที่คำนวณจากค่า base address ที่บวกกับค่า offset
        check_address(state, addr) #นำค่าที่ได้ไปเทียบกับใน memory ว่ามีจริงหรือไม่ หรือ ว่าเกินขอบเขตที่ควรจะมีหรือไม่
        state.reg[regB] = state.mem[addr] #ถ้ามีนำค่าที่ได้จาก memory[addr] ไปเก็บใน register B
        state.pc += 1

    elif opcode == SW:
        addr = state.reg[regA] + offset  #addr จะทำหน้าที่ในการเก็บตำแหน่งใน memory ที่คำนวณจากค่า base address ที่บวกกับค่า offset
        check_address(state, addr) #นำค่าที่ได้ไปเทียบกับใน memory ว่ามีจริงหรือไม่ หรือ ว่าเกินขอบเขตที่ควรจะมีหรือไม่
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


def check_address(state, addr):
    if addr < 0 or addr >= len(state.mem):
        print(f"error: memory address {addr} out of range", file=sys.stderr)
        sys.exit(1)