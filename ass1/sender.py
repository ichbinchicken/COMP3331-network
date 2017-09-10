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
# ----- TODO make statistic on page 6 -----
dataBytesTransed = 0
segmentSentNum = 0
retransmitted = 0
# ----- sending files variables -----
sendBase = 0
nextSequenceNum = 0
dupCount = 0
# ----- warm up -----
senderSocket = socket(AF_INET, SOCK_DGRAM)
logF = open("Sender_log.txt", "a")
try:
    f = open(file, "rb")
    fileToSend = f.read()
    f.close
except IOError:
    stderr.write(file+": File doesn't exist!\n")
    exit(1)
# ----- class -----
# multi threading classes:
class STPTimer(object):
    def __init__(self, interval, timeOutEvent):
        self.interval = interval
        self.timer = None
        self.timeOutEvent = timeOutEvent
    def start(self):
        self.timer = threading.Timer(self.interval, self.timeoutResend) # arg1:lifetime, arg2:func called when timeout
        self.timer.start()
        print("timer starting")
    def restart(self):
        self.timer.cancel()
        time.sleep(0.015)
        self.start()  
    def timeoutResend(self):
        oldNextSeqNum = nextSequenceNum
        Sending(sendBase)
        self.start()
        sequenceNum = oldNextSeqNum
    def alive(self):
        return self.timer.is_alive()
    def kill(self):
        self.timer.cancel()
        time.sleep(0.015)
# ----- others -----
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

def HandShaking(header, data):
    global sequenceNum, segmentSentNum, dataBytesTransed
    headerBytes = LonglongToBytes(header)
    dataBytes = data.encode('ascii')
    joinedBytes = JoinBytes(headerBytes, dataBytes)
    senderSocket.sendto(joinedBytes, (receiverName, receiverPort))
    WritingLog(header.segments, "snd")
    sequenceNum += 1 if (len(data) == 0) else len(data)
    # log file variables:
    segmentSentNum += 1 if (len(data) != 0) else 0
    dataBytesTransed += len(data)

def HandShakingRcv():
    (rcvMsgBytes, rcv_addr) = senderSocket.recvfrom(2048)
    rcvMsgInt = BytesToLonglong(rcvMsgBytes)
    rcvMsg_header = InitHeaderByInt(rcvMsgInt)
    WritingLog(rcvMsg_header.segments, "rcv") 
def SendingFile(i): 
    header = InitHeaderBySeg(DATA,len(data),i,acknowledgeNum,MWS) 
def ReceivingFile(done):
    global sendBase,dupCount
    while True:
        (msg, receiver_addr) = senderSocket.recvfrom(2048)
        recvHeader = InitHeaderByInt(BytesToLonglong(msg))
        recvNum = recvHeader.segments.acknum
        WritingLog(recvHeader.segments, "rcv")
        if sendBase < recvNum:
            sendBase = recvNum
            dupCount = 0
            timer.restart()
            if recvNum == len(fileToSend):
                done.set()
                exit(0)
        elif sendBase == recvNum:
            dupCount += 1
            if dupCount == 3:
                dupCount = 0
                timer.restart()
                SendingFile(sendBase)
def Statistic():
   logF.write("Amount of Data Transferred is "+dataBytesTransed+" bytes")
   logF.write("Num of Data Segments Sent(excluding retransmissions): "+segmentSentNum)
# ----- three-way handshaking -----
# sender -> recver
bTime = time.time()
header = InitHeaderBySeg(SYN,0,sequenceNum,0,MWS)
HandShaking(header, "")

#  recver -> sender
HandShakingRcv()

#sender -> recver
header = InitHeaderBySeg(ACK,0,sequenceNum,1,MWS) 
HandShaking(header, "")
sequenceNum -= 1 # as in example log file, seqNum doesn't change
                 # at the end of handshaking/starting sending files

# ----- Sending files -----
# sequenceNum = 1
# nextSequenceNum = 0
# sendBase = 0
# creating events 
done = Event()
# creating threading
timer = STPTimer(timeOut)
recvThreading = Thread(name='recv',target=ReceivingFile,args=(done,))

while True:
    if done.isSet():
        timer.kill()
        break
    if not timer.alive():
        timer.start()
    if nextSequenceNum < sendBase + MWS:
        for i in range(nextSequenceNum, min(sendBase+MWS,len(fileToSend)):
            SendingFile(i)
senderSocket.close()
