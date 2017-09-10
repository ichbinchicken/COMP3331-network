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

# repeating timer class
class STPTimer(object):
    def __init__(self, interval, event):
        self.interval = interval
        self.timer = None
        self.timout_event = event
    def start(self):
        self.timer = threading.Timer(self.interval, self.timeout)
        self.timer.start()
        print("timer starting")

    def restart(self):
        self.timer.cancel()
        time.sleep(0.01)
        self.start()  

    def timeout(self):
        self.timeout_event.set()
    def alive(self):
        return self.timer.is_alive()
    def kill(self):
        self.timer.cancel()
        time.sleep(0.01)
# receive ack
def STP_receive(ack_received):
    global send_base, next_seq
    while send_base < 10:
        ack_msg, receiver_addr = sender_socket.recvfrom(2048) 
        y = int.from_bytes(ack_msg, byteorder='big')
        if y > send_base:
            send_base = y
            #if send_base < next_seq:
                #timer.restart()
            timer.restart()
            ack_received.set()
def Resend(resend_event):
    global send_base
    resend_event.wait()
    send(send_base)
def send(i):
    global send_base, next_seq
    sender_socket.sendto(bytes([i]), (receiver_host_ip, receiver_port)) 
    next_seq = send_base+1
    print("send(i): sending %d" % i)


timer = STPTimer(2)
ack_received_event = threading.Event()
timeout_event = threading.Event()
resend_event = threading.Event()
recv_thread = threading.Thread(target=STP_receive, args=(ack_received,))
recv_thread.start()

# send data
timer.start()
send(send_base)
while send_base < 10:
    try:
        ack_received.wait()
        if not timer.alive():
            timer.start()
        if (send_base < 10):
            send(send_base)
            ack_received.clear()
            print("called send in main")
        #sender_socket.sendto(bytes([send_base]), (receiver_host_ip, receiver_port)) 
        #next_seq += 1
    except STPTimeoutException:
        print("time out!")
        #time.sleep(0.01)
        if send_base < next_seq:
            next_seq_old = next_seq
            timer.start()
            send(send_base)
            print("called send in time out")
            next_seq = next_seq_old

timer.kill()
recv_thread.join()
sender_socket.close()