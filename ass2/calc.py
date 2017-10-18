#!/usr/bin/python3
import sys
import math

total = 0

for line in sys.stdin:
    _, _, _, duration = line.split()
    total += math.floor(float(duration)*int(sys.argv[1]))

print(total)