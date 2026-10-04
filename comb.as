        lw      0       1       n           r1 = n
        lw      0       2       r           r2 = r
        lw      0       5       stackp      r5 = stack pointer (grows upward)
        lw      0       4       combad      r4 = address of comb
        jalr    4       7                   call comb(n, r), return address in r7
        halt                                result is already in r3
comb    lw      0       6       four        reserve a 4-word frame
        add     5       6       5           sp = sp + 4
        sw      5       7       -4          save return address
        sw      5       1       -3          save n
        sw      5       2       -2          save r
        beq     2       0       base        r == 0 -> 1
        beq     1       2       base        n == r -> 1
        lw      0       6       neg1
        add     1       6       1           n - 1
        lw      0       4       combad
        jalr    4       7                   r3 = comb(n-1, r)
        sw      5       3       -1          keep result of first call
        lw      5       1       -3          restore n
        lw      5       2       -2          restore r
        lw      0       6       neg1
        add     1       6       1           n - 1
        add     2       6       2           r - 1
        lw      0       4       combad
        jalr    4       7                   r3 = comb(n-1, r-1)
        lw      5       6       -1          r6 = result of first call
        add     3       6       3           r3 = sum of both calls
        beq     0       0       done
base    lw      0       3       one         base case returns 1
done    lw      5       7       -4          restore return address
        lw      0       6       neg4
        add     5       6       5           sp = sp - 4 (pop frame)
        jalr    7       6                   return
n       .fill   5
r       .fill   2
one     .fill   1
neg1    .fill   -1
four    .fill   4
neg4    .fill   -4
combad  .fill   comb
stackp  .fill   stack
stack   .fill   0