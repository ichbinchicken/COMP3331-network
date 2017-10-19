#!/usr/bin/python3
import sys
import math

total = 0

for line in sys.stdin:
    _, src, dest, duration = line.split()
    num = math.floor(float(duration)*int(sys.argv[1]))
    total += num
    print(src+" "+dest+" "+str(num))

print(total)