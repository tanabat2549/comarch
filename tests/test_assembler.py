import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSEMBLER = os.path.join(ROOT, "assembler.py")

cases = [
    # error 
    ("1. undefined label",       "\tlw 0 1 nolabel\n\thalt\n", 1),
    ("2. duplicate label",       "start add 1 2 1\nstart halt\n", 1),
    ("3. offset เกิน (32768)",    "\tlw 0 1 32768\n\thalt\n", 1),
    ("3. offset เกิน (-32769)",   "\tlw 0 1 -32769\n\thalt\n", 1),
    ("4. opcode ไม่รู้จัก (mul)",  "\tmul 1 2 3\n\thalt\n", 1),

    # error เพิ่มเติมที่โค้ดตรวจ
    ("5. label ยาวเกิน 6",        "toolonglabel add 1 2 1\n", 1),
    ("6. label ขึ้นต้นด้วยเลข",    "1abc add 1 2 1\n", 1),
    ("7. label มีอักขระพิเศษ",     "my_lbl add 1 2 1\n", 1),
    ("8. register เกิน (8)",      "\tadd 8 1 2\n", 1),
    ("9. register ติดลบ",         "\tadd -1 1 2\n", 1),
    ("10. register เป็น label",   "five add five 1 2\n", 1),
    ("11. field ขาด",             "\tadd 1 2\n", 1),
    ("12. label ไม่มี instruction", "lonely\n\thalt\n", 1),
    ("13. .fill ไม่มีค่า",         "\t.fill\n", 1),
    ("14. .fill เกิน 32 บิต",      "\t.fill 2147483648\n", 1),

    #  boundary
    ("15. label ยาว 6 พอดี",       "abcdef add 1 2 1\n\thalt\n", 0),
    ("16. offset 32767",         "\tlw 0 1 32767\n\thalt\n", 0),
    ("17. offset -32768",        "\tlw 0 1 -32768\n\thalt\n", 0),
    ("18. register 7",           "\tadd 7 7 7\n\thalt\n", 0),
    ("19. .fill 2147483647",     "\t.fill 2147483647\n", 0),
    ("20. .fill -2147483648",    "\t.fill -2147483648\n", 0),
    ("21. มี comment ท้ายบรรทัด",  "\tadd 1 2 3 this is a comment\n\thalt\n", 0),
]

passed = 0
with tempfile.TemporaryDirectory() as tmp:
    for name, source, expected in cases:
        infile = os.path.join(tmp, "in.as")
        outfile = os.path.join(tmp, "out.mc")
        with open(infile, "w", newline="\n") as f:
            f.write(source)

        result = subprocess.run(
            [sys.executable, ASSEMBLER, infile, outfile],
            capture_output=True, text=True,
        )
        ok = result.returncode == expected
        passed += ok
        message = result.stderr.strip().splitlines()
        message = message[0] if message else ""
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        print(f"       exit code: {result.returncode} (expected: {expected})")
        if message:
            print(f"       stderr   : {message}")

print(f"\nผ่าน {passed}/{len(cases)}")