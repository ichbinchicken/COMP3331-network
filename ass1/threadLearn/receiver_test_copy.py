#!/usr/bin/python3

from socket import *
from sys import *
import time
import random
import math

# open socket
server_port = int(argv[1])
filename = argv[2]
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))
print("Receiver is open...")
buffer = []
MSS = 40
MWS = 200
MNS = math.ceil(MWS/MSS) # maximum num of segments
f = open(filename, "ab") # a: append b:writing in bytes

recv_num_last = -1
while True:
    msg, sender_ip = server_socket.recvfrom(2048)
    i = random.randrange(5)
    (recv_numBytes, string) = msg.split('\x20', 1)
    recv_num = recv_numBytes.decode()
    recv_num = int(recv_num) 
    if (recv_num - 1) != recv_num_last:  # not receiving last
        if (i < 3):
            if recv_num not in dict(buffer): # if ack not received on sender side, sender sent again
                buffer.append((recv_num, string))
                print(buffer)
            server_socket.sendto(bytes([recv_num_last+1]), sender_ip)
            print("msg recv'd: %d, ack num: %d" % (recv_num, recv_num_last+1))
    else:
        if (i < 3):
            buffer.sort()
            last = recv_num
            f.write(string)
            while len(buffer) != 0 and buffer[0] == last+1:
                (last, stringToWrite) = buffer.pop(0)  
                f.write(stringToWrite)
            server_socket.sendto(bytes([last+1]), sender_ip)
            recv_num_last = last
            print("msg recv'd: %d, ack num: %d" % (recv_num, last+1))
