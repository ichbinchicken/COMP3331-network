from socket import *
import threading
import time
from sys import *
# open socket
receiver_host_ip = argv[1]
receiver_port = int(argv[2])
sender_socket = socket(AF_INET, SOCK_DGRAM)

next_seq = 0
send_base = 0
mws = 3

# exception

# repeating timer class
class STPTimer():

    #class STPTimeoutException(Exception):
    #    pass
    
    def __init__(self, interval, time_out):
        self.interval = interval
        self.timeout_event = time_out
        self.timer = None
    
    def stop(self, *args):
        self.timer.cancel()
        time.sleep(0.01)

    def start(self):
        self.timer = threading.Timer(self.interval, self.timeout)
        self.timer.start()
        print("timer starting")

    def restart(self):
        self.stop()
        self.start()  

    def timeout(self, *args):
        self.timeout_event.set()
        #raise self.STPTimeoutException

    def alive(self):
        return self.timer.is_alive()

# receive ack
def STP_receive(ack_received, done):
    global send_base, next_seq
    while True:
        ack_msg, receiver_addr = sender_socket.recvfrom(2048) 
        y = int.from_bytes(ack_msg, byteorder='big')
        if y > send_base:
            send_base = y
            timer.restart() #restart
            if y==10:   #stop at 10
                done.set()
            ack_received.set()

def send(i):
    global send_base, next_seq
    sender_socket.sendto(bytes([i]), (receiver_host_ip, receiver_port)) 
    next_seq = i+1
    print("send(i): sending %d" % i)

def STP_resend(timeout): 
    global send_base, next_seq
    while True:
        timeout.wait()
        print("time out!")

        #time.sleep(0.01)
        if send_base < next_seq:
            next_seq_old = next_seq
            timer.start()
            send(send_base)
            print("called resend after timeout")
            next_seq = next_seq_old
        timeout.clear()

# exit event
done = threading.Event()

# resend on timeout thread
timeout = threading.Event()
timer = STPTimer(2, timeout)
resend_thread = threading.Thread(name="resend", target=STP_resend, args=(timeout,))
resend_thread.daemon = True
resend_thread.start()

# receiving thread
ack_received = threading.Event()
recv_thread = threading.Thread(name="recv", target=STP_receive, args=(ack_received, done))
recv_thread.daemon = True
recv_thread.start()

# send data
timer.start()
for i in range(send_base, send_base+mws, 1):
    send(i)
while True:
    ack_received.wait()
    if done.isSet():
        timer.stop()
        print("all done")
        exit(0)
    if not timer.alive():
        timer.start()
    if next_seq < send_base+mws:
        for i in range(next_seq, min(send_base+mws, 10), 1):
            send(i)
    ack_received.clear()
    print("called send in main")
    #sender_socket.sendto(bytes([send_base]), (receiver_host_ip, receiver_port)) 
    #next_seq += 1

#recv_thread.join()
#resend_thread.join()
sender_socket.close()