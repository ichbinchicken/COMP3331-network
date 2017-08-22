#!/usr/bin/python
from __future__ import print_function
from socket import *
from time import *
import sys
req_array = []
segments = []
boolean = True
try:
    int(sys.argv[1])
except ValueError:
    boolean = False

if (boolean == False):
   host, port = ('', 1025)
elif ((len(sys.argv) < 2) or (int(sys.argv[1]) < 0) or (int(sys.argv[1]) > 65535)):
    host, port = ('', 1025)
else:
    host, port = ('', int(sys.argv[1]))

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((host, port))
serverSocket.listen(1)
print ('Serving HTTP on Port %s ...' % port)
while True:
    clientConnection, clientAddress = serverSocket.accept()
    request = clientConnection.recv(1024)
    print (request)
    req_array = request.split('\n', 1)
    segments = req_array[0].split()
    #print("Segments: ", end="")
    #print(segments)
    #print("=======")
    try:
        f = open(segments[1][1:], 'r')
        content = f.read()
        http_response = 'HTTP/1.1 200 OK\r\n'
        date = "Date: "+ctime()+'\r\n'
        content_len = "Content-Length: "+str(len(content))+'\r\n'
        clientConnection.sendall(http_response+date+content_len+'\r\n'+content)
        f.close()
        clientConnection.close()
    except IndexError:
        clientConnection.close()
    except IOError: 
        http_response = 'HTTP/1.1 404 Not Found\r\n'
        date = "Date: "+ctime()+'\r\n'
        clientConnection.sendall(http_response+date+'\r\n'+"HTTP 404 Not Found!\n")
        clientConnection.close()
