'''
import re
def list():
    return [1,2,3]

f = open("topology.txt", "r")
for line in f:
    (i,t,d,c) = re.split(" ", line)
    print(t)
l = list()
print(l)
'''
import sys
l = [1,2,3]
for i in l:
    d = [False] * i
print(d)
print(l)
print(ord(sys.argv[1]))

