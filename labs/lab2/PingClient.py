#!/usr/bin/python
from __future__ import print_function
from sys import *
from socket import *
from time import *

s = socket(AF_INET, SOCK_DGRAM) #constructor
host = argv[1]
port = int(argv[2])
addr = (host, port)
s.settimeout(1.1)
s.connect((addr))
for i in range (0,10):
    a = time()
    s.send('PING '+str(i)+' '+ctime()+' '+"\r\n")
    try:
        s.recv(1024)
        b = time()
        print("ping to %s, seq = %d, rrt = %d ms" %(host, i, (b-a)*1000));
    except timeout:
        print ("", end ='')
s.close()
