        lw      0       1       mcand   $1 = mcand (ตัวตั้ง จะถูก shift ซ้ายทุกรอบ)
        lw      0       2       mplier  $2 = mplier (ตัวคูณ ใช้ดูทีละ bit)
        lw      0       3       pos1    $3 = mask = 1 (ไว้ทดสอบ bit ทีละตัว)
        add     0       0       4       $4 = result = 0
        lw      0       5       neg16   $5 = counter = -16 (นับขึ้นจนถึง 0)
        lw      0       7       pos1    $7 = 1 (ค่าคงที่ ใช้เพิ่ม counter)
loop    nand    2       3       6       $6 = NOT (mplier AND mask)
        nand    6       6       6       $6 = mplier AND mask (NAND ซ้ำ = NOT)
        beq     6       0       skip    ถ้า bit นี้เป็น 0 ไม่ต้องบวก
        add     4       1       4       result = result + (mcand << i)
skip    add     1       1       1       mcand = mcand * 2 (shift ซ้าย 1 bit)
        add     3       3       3       mask = mask * 2 (เลื่อนไปดู bit ถัดไป)
        add     5       7       5       counter = counter + 1
        beq     5       0       done    ครบ 16 bit แล้วออกจากลูป
        beq     0       0       loop    ยังไม่ครบ วนต่อ
done    add     4       0       1       $1 = result (โจทย์บังคับให้ผลอยู่ register 1)
        halt
mcand   .fill   32766
mplier  .fill   10383
pos1    .fill   1
neg16   .fill   -16