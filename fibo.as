        lw      0       5       n           # reg[5] = N (เป้าหมาย)
        lw      0       1       zero        # reg[1] = a = 0 (ค่าเริ่มต้น F(0))
        lw      0       2       one         # reg[2] = b = 1 (ค่าเริ่มต้น F(1))
        lw      0       4       zero        # reg[4] = i = 0 (ตัวนับรอบ)
loop    beq     4       5       done        # ถ้าตัวนับ i == N ให้จบการทำงาน
        add     1       2       3           # reg[3] = a + b (คำนวณค่าถัดไป)
        add     0       2       1           # a = b (อัปเดต a)
        add     0       3       2           # b = a + b (อัปเดต b)
        lw      0       6       one         # โหลดเลข 1 มาเตรียมบวก
        add     4       6       4           # i = i + 1
        beq     0       0       loop        # กระโดดกลับไปเริ่ม loop
done    add     0       1       3           # นำผลลัพธ์สุดท้าย (a) มาใส่ reg[3] เพื่อส่งออก
        halt
zero    .fill   0
one     .fill   1
n       .fill   6                           # F(N) อื่น ๆ โดยที่ N ห้ามติดลบ