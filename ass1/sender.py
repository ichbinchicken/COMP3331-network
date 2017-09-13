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
receiverHost = argv[1]
receiverPort = int(argv[2])
fileName = argv[3]
MWS = int(argv[4])
MSS = int(argv[5])
timeOut = int(argv[6])
seqNum = 0
pdrop = float(argv[7])
seedNum = int(argv[8])
random.seed(seedNum)
addr = (receiverHost, receiverPort)
# ----- make statistic -----
dataBytesTransed = 0
segmentSentNum = 0
retransmittedNum = 0
droppedNum = 0
dupACK = 0
# ----- sending files variables -----
sendBase = 0
nextseqNum = 0
dupCount = 0
# ----- open file -----
senderSocket = socket(AF_INET, SOCK_DGRAM)
logF = open("Sender_log.txt", "a")
try:
    f = open(fileName, "rb")
    fileBytes = f.read()
    f.close
except IOError:
    stderr.write(file+": File doesn't exist!\n")
    exit(1)

FILE_LEN = len(fileBytes)

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

# multi threading classes:
class STPTimer(object):
    id = 0
    def __init__(self, interval):
        self.interval = interval
        self.timer = None
    def start(self):
        self.timer = Timer(self.interval, self.timeoutResend()) # arg1:lifetime, arg2:func called when timeout
        self.timer.start()
        print("timer starting")
    def restart(self):
        self.timer.cancel()
        time.sleep(0.1)
        #assert not self.timer.is_alive()
        # assert self.timer.finished()
        self.timer = Timer(self.interval, self.timeoutResend()) # arg1:lifetime, arg2:func called when timeout
        self.timer.start()
    def timeoutResend(self):
        STPTimer.id += 1
        currIdx = STPTimer.id
        def f():
            if STPTimer.id != currIdx:
                return
            global retransmittedNum,sendBase,nextseqNum,lock
            if sendBase < nextseqNum and sendBase < FILE_LEN:
                print("resend in timer, sendbase=%d, nextseq=%d, time=%f" % (sendBase, nextseqNum, time.time()))
                ret()
                retransmittedNum += 1
        return f
    def alive(self):
        return self.timer != None and self.timer.is_alive()
    def kill(self):
        if self.timer != None and self.timer.is_alive():
            print("got here")
            print(self.timer)
            self.timer.cancel()
            time.sleep(0.1)
            assert not self.timer.is_alive()

# ----- subroutines -----
def ret():
    global nextseqNum, sendBase, timer,lock
    lock.acquire()
    oldNextSeqNum = nextseqNum
    SendingFile(sendBase)
    nextseqNum = oldNextSeqNum
    timer.restart()
    lock.release()
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
    diff = (eTime - bTime)*1000
    if int(diff) == 0:
        logF.write("%-4s %-6.4f %-3s %-5d %-5d %-5d\n"\
                % (msg,diff,CheckingFlags(seg.flags),\
                    seg.seqnum,seg.length,seg.acknum))
    else:    
        logF.write("%-4s %-6.5g %-3s %-5d %-5d %-5d\n"\
                % (msg,diff,CheckingFlags(seg.flags),\
                    seg.seqnum,seg.length,seg.acknum))

def JoinBytes(b1, b2):
    return b"".join([b1,b2])

def HandShaking(newHeader):
    global seqNum
    headerBytes = LonglongToBytes(newHeader)
    senderSocket.sendto(headerBytes, addr)
    WritingLog(header.segments, "snd")
    seqNum += 1

def HandShakingRcv():
    (rcvMsgBytes, rcv_addr) = senderSocket.recvfrom(2048)
    (rcvMsgInt,) = BytesToLonglong(rcvMsgBytes)
    rcvMsg_header = InitHeaderByInt(rcvMsgInt)
    WritingLog(rcvMsg_header.segments, "rcv") 

def SendingFile(i): # i is ready to send
    global nextseqNum,dataBytesTransed,droppedNum,seqNum
    prob = random.random()
    print("prob is %f" %prob)
    seqNum = i + 1
    length = min(FILE_LEN-i,MSS)
    print("datalength is %d" % length)
    print("seqNum is %d" % seqNum)
    sendingHeader = InitHeaderBySeg(DATA,length,seqNum,1,MWS)
    headerBytes = LonglongToBytes(sendingHeader)
    dataBytes = fileBytes[i:i+length]
    joinBytes = JoinBytes(headerBytes,dataBytes)
    nextseqNum += length
    if prob > pdrop:
        # sending segments
        senderSocket.sendto(joinBytes,addr)
        #dataBytesTransed += length
        print("seq: %d, data: %s" %(seqNum, dataBytes.decode('ascii')))
        WritingLog(sendingHeader.segments,"snd")
    else:
        droppedNum += 1
        print("DROPPED")
        WritingLog(sendingHeader.segments,"drop")
def ReceivingFile(done): # receiver only sends a header containing acknum
    global sendBase,dupCount,dupACK,nextseqNum, timer
    while True:
        (msg, receiver_addr) = senderSocket.recvfrom(2048)
        (msgInt,) = BytesToLonglong(msg)
        recvHeader = InitHeaderByInt(msgInt)
        recvNum = recvHeader.segments.acknum - 1
        print("ack recv'd %d" % recvNum)
        WritingLog(recvHeader.segments, "rcv")
        if sendBase < recvNum:
            sendBase = recvNum # this means sender has received receiver's acknum and shift window to the next.
            dupCount = 0
            timer.restart()
            if recvNum == FILE_LEN:
                print("RECVNUM == FILE_LEN")
                done.set()
                exit(0)
        elif sendBase == recvNum:
            dupCount += 1
            dupACK += 1
            if dupCount == 3:
                dupCount = 0
                lock.acquire()
                timer.restart()
                nextSeqOld = nextseqNum
                SendingFile(sendBase)
                nextseqNum = nextSeqOld
                lock.release()
                print("fast ret")
def Statistic():
    global dataBytesTransed,segmentSentNum,droppedNum,retransmittedNum, dupACK
    logF.write("Number of Data Transferred: %d\n" % dataBytesTransed)
    logF.write("Number of Data Segments Sent(excluding retransmissions): %d\n" % segmentSentNum)
    logF.write("Number of Packets Dropped: %d\n" % droppedNum)
    logF.write("Number of Retransmitted Segments: %d\n" % retransmittedNum)
    logF.write("Number of Duplicate Acknowledgements: %d\n" % dupACK)



# ----- three-way handshaking -----
# sender -> recver
bTime = time.time()
header = InitHeaderBySeg(SYN,0,0,0,MWS)
HandShaking(header)

#  recver -> sender
HandShakingRcv()

#sender -> recver
header = InitHeaderBySeg(ACK,0,seqNum,1,MWS) 
HandShaking(header)
seqNum -= 1 # as in example log file, seqNum doesn't change
                 # at the end of handshaking/starting sending files
print("after handshaking seq num is %d" % seqNum)
# ----- Sending files -----
# seqNum = 1
# nextseqNum = 0
# sendBase = 0
# creating events 
done = Event()
# creating threading
timer = STPTimer(timeOut/1000)
recvThreading = Thread(name='recv',target=ReceivingFile,args=(done,))
recvThreading.start()
lock = RLock()
while True:
    if done.isSet():
        timer.kill()
        print("File transferred!")
        if (timer.alive()):
            print("timer alive after kill")
        else:
            print("timer killed")
        break
    if sendBase < FILE_LEN and not timer.alive():
        timer.start()
        print("timer starting in main")
    if nextseqNum < sendBase + MWS:
        lock.acquire()
        i = nextseqNum
        while i < min(sendBase+MWS,FILE_LEN):
            SendingFile(i)
            l = min(FILE_LEN-i,MSS)
            dataBytesTransed += l
            segmentSentNum += 1
            i += MSS
            print("called send in main")
        lock.release()
# ending:
header = InitHeaderBySeg(FIN,0,seqNum,1,MWS)
HandShaking(header)

#  recver -> sender
HandShakingRcv()

#sender -> recver
header = InitHeaderBySeg(ACK,0,seqNum,2,MWS) 
HandShaking(header)

Statistic()
logF.close()

senderSocket.close()
