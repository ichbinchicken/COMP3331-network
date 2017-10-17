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
a = 1
if a == 1: print("hahah")
print(d)
print(l)

def nothing():
    return []

print("nothing is",nothing()) 


