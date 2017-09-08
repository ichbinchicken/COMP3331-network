#!/usr/local/bin/python3
from ctypes import *
import sys
import struct
SYN = 0b1000
ACK = 0b0100
FIN = 0b0010
DATA = 0b0001
def CheckingFlags(combo):
    return {
        SYN: "S",
        ACK: "A",
        FIN: "F",
        DATA: "D",
        (SYN|ACK): "SA",
        (FIN|ACK): "FA",
    }[combo]
class Segments(Structure):
       _fields_ = [("flags", c_uint64, 4),  # SYN = 1000, ACK = 0100, FIN = 0010, DATA = 0001
                   ("length", c_uint64, 13),  # maximum length(MSS) is 536.
                   ("seqnum", c_uint64, 16),      
                   ("acknum", c_uint64, 16),
                   ("rwnd", c_uint64, 16)]    # maximum window size is 2^16
class Header(Union):
       _fields_ = [("segments", Segments),
                  ("integer",c_uint64)]
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

header1 = InitHeaderByInt(0x14000000000004)
header2 = InitHeaderBySeg(0x4,0,0,0,0x14)
print("header1 things...")
dataBytes1 = LonglongToBytes(header1)
print(dataBytes1)
data1 = struct.unpack('q', dataBytes1)
print(hex(data1[0]))
print("header2 things...")
dataBytes2 = LonglongToBytes(header2)
print(dataBytes2)
data2 = BytesToLonglong(dataBytes2)
print(hex(data2[0]))
print(type(FileToBytes("test1.txt")))
print(dataBytes2[0:2])
print("checking flags...")
print(CheckingFlags((SYN|ACK)))