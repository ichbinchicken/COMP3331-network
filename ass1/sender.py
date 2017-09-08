#!/usr/bin/python3
from sys import *
from socket import *
from ctypes import *
from threading import *
import time
import struct
# global variables:
SYN = 0b1000
ACK = 0b0100
FIN = 0b0010
DATA = 0b0001
receiverName = argv[1]
receiverPort = int(argv[2])
fileName = argv[3]
MWS = int(argv[4])
MSS = int(argv[5])
timeOut = int(argv[6])
pdrop = int(argv[7])
seed = int(argv[8])
sequenceNum = 0
acknowledgeNum = 0
# ----- TODO make statistic on page 6 -----
dataBytesTransed = 0
segmentSentNum = 0
# ----- sending files variables -----
sendBase = 0
# ----- warm up -----
senderSocket = socket(AF_INET, SOCK_DGRAM)
senderSocket.settimeout(timeOut)
logF = open("Sender_log.txt", "a+")
# ----- class -----
class MyThread(Thread):
    def __init__(self, func, args, name=''):
        Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
    def run(self):
        self.func(*self.args)

class Segments(Structure):
    _fields_ = [("flags", c_uint64, 4),  # SYN = 1000, ACK = 0100, FIN = 0010 DATA = 0001
                ("length", c_uint64, 12),  # maximum length(MSS) is 536.
                ("seqnum", c_uint64, 16),
                ("acknum", c_uint64, 16),
                ("rwnd", c_uint64, 16)]    # maximum window size is 2^16.

class Header(Union):
    _fields_ = [("segments", Segments),
               ("integer",c_uint64)]
# ----- subroutines -----
def FileToBytes(file):
    try:
        f = open(file, "r")
        fileToSend = f.read()
        f.close
    except IOError:
        stderr.write(file+": File doesn't exist!\n")
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
        SYN: "S",
        ACK: "A",
        FIN: "F",
        DATA: "D",
        (SYN|ACK): "SA",
        (FIN|ACK): "FA",
    }[combo]

def WritingLog(seg, msg):
    eTime = time.time()
    logF.write("%-4s %-6.5g %-3s %-5d %-5d %-5d\n"\
            % (msg,(eTime-bTime)*1000,CheckingFlags(seg.flags),\
                seg.seqnum,seg.length,seg.acknum))

def JoinBytes(b1, b2):
    return b"".join([b1,b2])

def Sending(header, data, repeat):
    global sequenceNum, segmentSentNum, dataBytesTransed
    headerBytes = LonglongToBytes(header)
    dataBytes = data.encode('ascii')
    joinedBytes = JoinBytes(headerBytes, dataBytes)
    senderSocket.sendto(joinedBytes, (receiverName, receiverPort))
    if (repeat == False):
        WritingLog(header.segments, "snd")
        sequenceNum += 1 if (len(data) == 0) else len(data)
        segmentSentNum += 1 if (len(data) != 0) else 0
        dataBytesTransed += len(data)

def Receiving():
    global acknowledgeNum
    (rcvMsgBytes, rcv_addr) = senderSocket.recvfrom(2048)
    rcvMsgInt = BytesToLonglong(rcvMsgBytes)
    rcvMsg_header = InitHeaderByInt(rcvMsgInt)
    WritingLog(rcvMsg_header.segments, "rcv")
    if (CheckingFlags(rcvMsg_header.segments.flags) == "SA" \
        or CheckingFlags(rcvMsg_header.segments.flags) == "FA"):
        acknowledgeNum += 1
    return rcvMsg_header
def Statistic():
   logF.write("Amount of Data Transferred is "+dataBytesTransed+" bytes")
   logF.write("Num of Data Segments Sent(excluding retransmissions): "+segmentSentNum)
def dealWithACK():
    #TODO
# ----- three-way handshaking -----
# sender -> recver
bTime = time.time()
header = InitHeaderBySeg(SYN,0,sequenceNum,acknowledgeNum,MWS)
repeat = False
Sending(header, "",repeat)

#  recver -> sender
rcv_header = Receiving()

#sender -> recver
header = InitHeaderBySeg(ACK,0,sequenceNum,acknowledgeNum,MWS) 
Sending(header, "", False)
sequenceNum -= 1 # as in example log file, seqNum doesn't change
                 # at the end of handshaking/starting sending files

# ----- Sending files -----
# sequenceNum = 1
fileBytes = FileToBytes(fileName)
remainderBytes = len(fileBytes) % MSS
sendBase = sequenceNum
#while True:
#    print("yee")
#    time.sleep(3)
while (dataBytesTransed < len(fileBytes)):
    if (dataBytesTransed == len(fileBytes)):
        print("Transfer Complete!")
        break
    repeat = False
    if ((len(fileBytes) - dataBytesTransed) == remainderBytes):
        sent_header = InitHeaderBySeg(DATA,remainderBytes,sequenceNum,acknowledgeNum,MWS)
    else:
        sent_header = InitHeaderBySeg(DATA,MSS,sequenceNum,acknowledgeNum,MWS)
    #TODO: Sending(sent_header,,repeat)
    # ----- multi-threading part -----
    while True:
        try:
            # newThread = MyThread(target=dealWithACK, args=)
            # maybe put them in the thread:
            #rcv_header = Receiving()
            #if (CheckingFlags(rcv_header.segments.flags) == "A"):
            #    if (rcv_header.segments.acknum > sendBase):
            #        sendBase = rcv_header.segments.acknum
        except timeout:
            repeat = True
    #TODO:  Sending(sent_header,,repeat)
            WritingLog(sent_header,"drop")
            


# split into segments with MSS size each
senderSocket.close()
