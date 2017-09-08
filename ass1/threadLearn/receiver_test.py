#!/usr/bin/python3

from socket import *
from sys import *
import time
import random

# open socket
server_port = int(argv[1])
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))
print("Receiver is open...")

while True:
    msg, sender_ip = server_socket.recvfrom(2048)
    random.seed(42)
    i = random.randrange(3)
    #if (i<2):
    ack_num = int.from_bytes(msg, byteorder='big')
    server_socket.sendto(bytes([ack_num+1]), sender_ip)
    print("msg recv'd: %s, ack num: %d" % (ack_num, ack_num+1))
