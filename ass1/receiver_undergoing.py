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

def HandShaking(header, data):
    global sequenceNum
    headerBytes = LonglongToBytes(header)
    dataBytes = data.encode('ascii')
    joinedBytes = JoinBytes(headerBytes, dataBytes)
    server_socket.sendto(joinedBytes, (receiverName, receiverPort))
    WritingLog(header.segments, "snd")
    sequenceNum += 1


def HandShakingRcv():
    (rcvMsgBytes, rcv_addr) = server_socket.recvfrom(2048)
    rcvMsg_header = InitHeaderByInt(BytesToLonglong(rcvMsgBytes))
    WritingLog(rcvMsg_header.segments, "rcv") 
def ReceivingFile():
    (joinedBytes,sender_ip) = server.socket.recvfrom(2048)
    headerInt = Header()
    headerBytes = joinedBytes[0:8]
    dataBytes = joinedBytes[8:len(joinedBytes)]
    headerInt = BytesToLonglong(headerBytes)
    return (headerInt, dataBytes)

f = open(filename, "ab") # a: append b:writing in bytes
recv_num_last = -1
# ----- statistics -----
dataReceived = 0
dataSegmentReceived = 0

# handshaking:
HandShakingRcv()
sendingHeader = InitHeaderBySeg((SYN|ACK),0,0,1,MWS)
HandShaking(sendingHeader,"")
HandShakingRcv()

while True:
    #msg, sender_ip = server_socket.recvfrom(2048)
    #(recv_numBytes, string) = msg.split('\x20', 1)
    #recv_num = recv_numBytes.decode()
    recvHeader = Header()
    (recvheader, dataBytes) = ReceivingFile()
    recv_num = recvHeader.segments.seqnum
    if (recv_num - 1) != recv_num_last:  # not receiving last
        if recv_num not in dict(buffer): # if ack not received on sender side, sender sent again
            buffer.append((recv_num, string))
            print(buffer)
        server_socket.sendto(bytes([recv_num_last+1]), sender_ip)
        print("msg recv'd: %d, ack num: %d" % (recv_num, recv_num_last+1))
    else:
        buffer.sort()
        last = recv_num
        f.write(string)
        while len(buffer) != 0 and buffer[0] == last+1:
            (last, stringToWrite) = buffer.pop(0)  
            f.write(stringToWrite)
        server_socket.sendto(bytes([last+1]), sender_ip)
        recv_num_last = last
        print("msg recv'd: %d, ack num: %d" % (recv_num, last+1))


f.close()