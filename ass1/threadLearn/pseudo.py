import threading
import time
import logging
def dealWithACK(e,rcv_header):
    while True:
        event_is_set = e.wait()
        # TODO deal with ACK

#  -------------- useless stuff ------------
#def waitForTimeOut(e, byte):
#    while not e.isSet():
#        logging.debug('wait_for_event_timeout starting')
#        event_is_set = e.wait()
#        logging.debug('event set: %s', event_is_set)
#        if event_is_set:
#            # doing nothing?
#        else:
#            while True:
#                timeoutFlag = ReceivingBytes(TIMEOUT)
#                if (timeoutFlag):
#                    Sending(byte)
#                else:
#                    # calling dealWithACK function
#                    break
#def f3:

if __name__ = '__main__':
settimeout(timeout)

while (transferredBytes < TotoalBytes):
    t1 = threading.Thread(name='ack', target=dealWithACK, args=(e,rcv_header))
    t1.start()
    while True:
        try:
            ReceivingBytes(TIMEOUT)
            if (ack > base)
            e.set()
            break
        except timeout:
            Sending(byte)
    transferredBytes += len(data)*len(window)


