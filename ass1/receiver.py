#!/usr/bin/python3
from socket import *
from ctypes import *
from sys import *
import time
import struct
import random
import math

# open socket
server_port = int(argv[1])
filename = argv[2]
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))
print("Receiver is open...")
buffer = []
logF = open("Receiver_log.txt", "a")
# global variables:
SYN = 0b1000
ACK = 0b0100
FIN = 0b0010
DATA = 0b0001
sequenceNum = 0
# ----- class -----
class Segments(Structure):
    _fields_ = [("flags", c_uint64, 4),  # SYN = 1000, ACK = 0100, FIN = 0010 DATA = 0001
                ("length", c_uint64, 12),  # maximum length(MSS) is 536.
                ("seqnum", c_uint64, 16),
                ("acknum", c_uint64, 16),
                ("rwnd", c_uint64, 16)]    # maximum window size is 2^16.

class Header(Union):
    _fields_ = [("segments", Segments),
               ("integer",c_uint64)]
# ----- functions ----- 
def LonglongToBytes(h):
    return (struct.pack('q', h.integer))

def BytesToLonglong(b):
    return (struct.unpack('q', b))

def InitHeaderByInt(integer):
    header = Header()
    header.integer = integer
    return header

def InitHeaderBySeg(flags, length, seqnum, acknum, rwnd):
    header = Header()
    header.segments.flags = flags
    header.segments.length = length
    header.segments.seqnum = seqnum
    header.segments.acknum = acknum
    header.segments.rwnd = rwnd
    return header

def CheckingFlags(combo):
    return {
        SYN: "S",
        ACK: "A",
        FIN: "F",
        DATA: "D",
        (SYN|ACK): "SA",
        (FIN|ACK): "FA",
    }[combo]

def JoinBytes(b1, b2):
    return b"".join([b1,b2])
def WritingLog(seg, msg):
    eTime = time.time()
    logF.write("%-4s %-6.5g %-3s %-5d %-5d %-5d\n"\
            % (msg,(eTime-bTime)*1000,CheckingFlags(seg.flags),\
                seg.seqnum,seg.length,seg.acknum))

def HandShaking(header):
    global sequenceNum
    headerBytes = LonglongToBytes(header)
    server_socket.sendto(headerBytes, sender_ip)
    WritingLog(header.segments, "snd")
    sequenceNum += 1


def HandShakingRcv():
    global sender_ip
    (rcvMsgBytes, sender_ip) = server_socket.recvfrom(2048)
    (recvMsgInt,) = BytesToLonglong(rcvMsgBytes)
    #print(bin(recvMsgInt))
    rcvMsg_header = InitHeaderByInt(recvMsgInt)
    WritingLog(rcvMsg_header.segments, "rcv")
    return rcvMsg_header
def ReceivingFile():
    global sender_ip
    (joinedBytes,sender_ip) = server_socket.recvfrom(2048)
    headerInt = Header()
    headerBytes = joinedBytes[0:8]
    dataBytes = joinedBytes[8:]
    (headerInt.integer,) = BytesToLonglong(headerBytes)
    print(bin(headerInt.integer))
    return (headerInt, dataBytes)
def Sending(ack):
    global sender_ip
    recverHeader = InitHeaderBySeg(DATA,0,1,ack,0)
    recverHeaderBytes = LonglongToBytes(recverHeader)
    server_socket.sendto(recverHeaderBytes, sender_ip)

f = open(filename, "ab") # a: append b:writing in bytes
recv_num_last = 1
dataLength = 0
lastDataLength = 0
# ----- statistics -----
dataReceived = 0 
dataSegmentReceived = 0

# handshaking:
bTime = time.time()
HandShakingRcv()
sendingHeader = InitHeaderBySeg((SYN|ACK),0,0,1,0)
HandShaking(sendingHeader)
HandShakingRcv()
#print("================================================")
while True:
    (recvHeader, dataBytes) = ReceivingFile()
    #print("****below")
    #print(bin(recvHeader.integer))
    recv_num = recvHeader.segments.seqnum
    dataLength = recvHeader.segments.length
    print("recv_num is %d" % recv_num)
    if (recv_num - lastDataLength) != recv_num_last:  # not receiving last
        if recv_num not in dict(buffer): # if ack not received on sender side, sender sent again
            #buffer.append((recv_num, string))
            buffer.append((recv_num, dataBytes))
            print(buffer)
        Sending(recv_num_last+lastDataLength)
        #server_socket.sendto(bytes([recv_num_last+1]), sender_ip)
        print("msg recv'd: %d, ack num: %d" % (recv_num, recv_num_last+lastDataLength))
    else: #recv_num - lastDataLength == recv_num_last:
        buffer.sort()
        last = recv_num
        f.write(dataBytes)
        while len(buffer) != 0 and buffer[0][0] == last+len(dataBytes):
            print(len(buffer))
            (last, dataBytes) = buffer.pop(0)
            f.write(dataBytes)
            print("last = %d dataBytes = %s" % (last, dataBytes))
            #(last, stringToWrite) = buffer.pop(0)  
            #f.write(stringToWrite)
        #server_socket.sendto(bytes([last+1]), sender_ip)
        Sending(last+len(dataBytes))
        lastDataLength = len(dataBytes)
        recv_num_last = last
        print("elif msg recv'd: %d, ack num: %d" % (recv_num, last+lastDataLength))
'''
endHeader = HandShakingRcv()
sendingHeader = InitHeaderBySeg((FIN|ACK),0,0,1,0)
HandShaking(sendingHeader)
HandShakingRcv()
'''
f.close()