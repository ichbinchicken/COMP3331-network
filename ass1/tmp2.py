#!/usr/local/bin/python3
import sys
with open("newFile.txt", "a+") as f:
    f.write("%-4s %-6.5g %-3s %-5d %-5d %-5d" % ("rnd", float(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])))