#!/usr/bin/python3
from sys import *
from socket import *
from ctypes import *
from threading import *
import time
import struct
import random
# sequence number is the number you are sending
# next sequence number is the number you are GOING TO send in next time
# send base is the oldest not ack'd number
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
sequenceNum = 0
# ----- make statistic -----
dataBytesTransed = 0
segmentSentNum = 0
retransmittedNum = 0
droppedNum = 0
dupACK = 0
# ----- sending files variables -----
sendBase = 0
nextSequenceNum = 0
dupCount = 0
# ----- warm up -----
senderSocket = socket(AF_INET, SOCK_DGRAM)
logF = open("Sender_log.txt", "a")
try:
    f = open(fileName, "rb")
    fileBytes = f.read()
    f.close
except IOError:
    stderr.write(file+": File doesn't exist!\n")
    exit(1)
# ----- class -----
# multi threading classes:
class STPTimer(object):
    global retransmittedNum,sendbase,nextSequenceNum
    def __init__(self, interval):
        self.interval = interval
        self.timer = None
    def start(self):
        self.timer = Timer(self.interval, self.timeoutResend) # arg1:lifetime, arg2:func called when timeout
        self.timer.start()
        print("timer starting")
    def restart(self):
        self.timer.cancel()
        time.sleep(0.015)
        self.start()  
    def timeoutResend(self):
        global retransmittedNum
        oldNextSeqNum = nextSequenceNum
        SendingFile(sendBase)
        self.start()
        sequenceNum = oldNextSeqNum
        retransmittedNum += 1
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

def HandShaking(newHeader):
    global sequenceNum
    headerBytes = LonglongToBytes(newHeader)
    senderSocket.sendto(headerBytes, (receiverName, receiverPort))
    WritingLog(header.segments, "snd")
    sequenceNum += 1

def HandShakingRcv():
    (rcvMsgBytes, rcv_addr) = senderSocket.recvfrom(2048)
    (rcvMsgInt,) = BytesToLonglong(rcvMsgBytes)
    rcvMsg_header = InitHeaderByInt(rcvMsgInt)
    WritingLog(rcvMsg_header.segments, "rcv") 

def SendingFile(i): # i is ready to send TODO: datatransferred
    global nextSequenceNum,dataBytesTransed,droppedNum,sequenceNum
    pdrop = float(argv[7])
    seedNum = int(argv[8])
    random.seed(seedNum)
    prob = random.random()
    sequenceNum = i + 1
    length = min(len(fileBytes)-i,MSS)
    print(length)
    print(sequenceNum)
    sendingHeader = InitHeaderBySeg(DATA,length,sequenceNum,1,MWS)
    headerBytes = LonglongToBytes(sendingHeader)
    dataBytes = fileBytes[i:i+length]
    joinBytes = JoinBytes(headerBytes,dataBytes)
    nextSequenceNum += length
    if prob > pdrop:
        # sending segments
        senderSocket.sendto(joinBytes,(receiverName, receiverPort))
        dataBytesTransed += length
        print("seq: %d, data: %s" %(sequenceNum, dataBytes.decode('ascii')))
        WritingLog(sendingHeader.segments,"snd")
    else:
        droppedNum += 1
        WritingLog(sendingHeader.segments,"drop")

def ReceivingFile(done): # receiver only sends a header containing acknum
    global sendBase,dupCount,dupACK
    while True:
        (msg, receiver_addr) = senderSocket.recvfrom(2048)
        (msgInt,) = BytesToLonglong(msg)
        recvHeader = InitHeaderByInt(msgInt)
        recvNum = recvHeader.segments.acknum
        WritingLog(recvHeader.segments, "rcv")
        if sendBase < recvNum:
            sendBase = recvNum # this means sender has received receiver's acknum and shift window to the next.
            dupCount = 0
            timer.restart()
            if recvNum == len(fileBytes):
                done.set()
                exit(0)
        elif sendBase == recvNum:
            dupCount += 1
            dupACK += 1
            if dupCount == 3:
                dupCount = 0
                timer.restart()
                SendingFile(sendBase)
def Statistic():
    global dataBytesTransed,segmentSentNum,droppedNum,retransmittedNum, dupACK
    logF.write("Number of Data Transferred: "+dataBytesTransed+" bytes")
    logF.write("Number of Data Segments Sent(excluding retransmissions): "+segmentSentNum)
    logF.write("Number of Packets Dropped: "+droppedNum)
    logF.write("Number of Retransmitted Segments: "+retransmittedNum)
    logF.write("Number of Duplicate Acknowledgements: "+dupACK)
# ----- three-way handshaking -----
# sender -> recver
bTime = time.time()
header = InitHeaderBySeg(SYN,0,0,0,MWS)
HandShaking(header)

#  recver -> sender
HandShakingRcv()

#sender -> recver
header = InitHeaderBySeg(ACK,0,sequenceNum,1,MWS) 
HandShaking(header)
sequenceNum -= 1 # as in example log file, seqNum doesn't change
                 # at the end of handshaking/starting sending files
print("after handshaking seq num is %d" % sequenceNum)
# ----- Sending files -----
# sequenceNum = 1
# nextSequenceNum = 0
# sendBase = 0
# creating events 
done = Event()
# creating threading
timer = STPTimer(timeOut/1000)
recvThreading = Thread(name='recv',target=ReceivingFile,args=(done,))
recvThreading.start()
timer.start()
SendingFile(0)
while True:
    if done.isSet():
        timer.kill()
        print("File transferred!")
        break
    if not timer.alive():
        timer.start()
    if nextSequenceNum < sendBase + MWS:
        i = nextSequenceNum
        while i < min(sendBase+MWS,len(fileBytes)):
            SendingFile(i)
            segmentSentNum += 1
            i += min(MSS,len(fileBytes)-i)
        #for i in range(nextSequenceNum, min(sendBase+MWS,len(fileBytes), min(MSS,len(fileBytes)-i))):
        #    SendingFile(i)
        #    segmentSentNum += 1
# ending:
'''
header = InitHeaderBySeg(FIN,0,sequenceNum,1,MWS)
HandShaking(header, "")

#  recver -> sender
HandShakingRcv()

#sender -> recver
header = InitHeaderBySeg(ACK,0,sequenceNum,2,MWS) 
HandShaking(header)
'''
logF.close()

senderSocket.close()
