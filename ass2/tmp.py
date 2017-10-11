import re
def list():
    return [1,2,3]

f = open("topology.txt", "r")
for line in f:
    (i,t,d,c) = re.split(" ", line)
    print(t)
l = list()
print(l)
