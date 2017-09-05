#!/usr/bin/python3
from sys import *
from socket import *
from ctype import *
import time
import struct
# global variables:
receiverName = argv[1]
receiverPort = argv[2]
fileName = argv[3]
MWS = argv[4]
MSS = argv[5]
timeOut = argv[6]
pdrop = argv[7]
seed = argv[8]
# segment header
class Segments(Structure):
    _fields_ = [("flags", c_uint64, 4),  # SYN = 1000, ACK = 0100, FIN = 0010 DATA = 0001
                ("length", c_uint64, 12),  # maximum length(MSS) is 536.
                ("seqnum", c_uint64, 16),
                ("acknum", c_uint64, 16),
                ("rwnd", c_uint64, 16)]    # maximum window size is 2^16.
class Header(Union):
    _fields_ = [("segments", Segments),
               ("integer",c_uint64)]
# subroutines:
def FileToBytes(file):
    try:
        f = open(file, "r")
        fileToSend = f.read()
    except IOError:
        sys.stderr.write(file+": File doesn't exist!\n")
        exit(1)
    fileBytes = fileToSend.encode('ascii')
    return fileBytes 
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
        0b1000: "S",
        0b0100: "A",
        0b0010: "F",
        0b0001: "D",
        0b1100: "SA",
        0b0110: "FA",
    }[combo]
def WritingLog(seg, msg):
    with open("Sender_log.txt", "a+") as f:
        eTime = time.time()
        f.write("%-4s %-6.5g %-3s %-5d %-5d %-5d\n" 
                 % (msg,(eTime-bTime)*1000,CheckingFlags(seg.flags),
                    seg.seqnum,seg.length,seg.acknum))
def JoinBytes(b1, b2):
    # TODO
# main: 
senderSocket = socket(AF_INET, SOCK_DRAM)

# three-way handshaking:
# sender -> recver
bTime = time.time()
header = InitHeaderBySeg(0b1000,0,0,0,0) # SYN
headerBytes = LonglongToBytes(header)
data = ""
dataBytes = data.encode('ascii')
# TODO: 
# join headerBytes and dataBytes togother
# joinedBytes = 
senderSocket.sendto(joinedBytes, (receiverName, receiverPort))
WritingLog(header.segments, "snd")

# recver -> sender
(rcvMsgBytes, rcv_addr) = sendSocket.recvfrom(2048)
rcvMsgInt = BytesToLonglong(rcvMsgBytes)
rcvMsg_header = InitHeaderByInt(rcvMsgInt)
WritingLog(rcvMsg_header.segments, "rcv")

#sender -> recver
header = InitHeaderBySeg(0b0100,0,1,1) # ACK
headerBytes = LonglongToBytes(header)
data = ""
dataBytes = data.encode('ascii')
# TODO: 
# join headerBytes and dataBytes togother
# joinedBytes = 
senderSocket.sendto(joinedBytes, (receiverName, receiverPort))
WritingLog(header.segments, "snd")

# Sending files:

fileBytes = FileToBytes(fileName)
while True:
    headerToSend = InitHeaderBySeg()
    if ()
# split into segments with MSS size each

senderSocket.close()
