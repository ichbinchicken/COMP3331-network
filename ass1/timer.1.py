import threading
import time

def f():
    print("timeout: "+str(time.time()))

print("start: "+str(time.time()))
timer = threading.Timer(2, f)
timer.start()
print(timer)
time.sleep(0.5)
timer.cancel()
time.sleep(0.01)
assert timer == None
print(timer)
print(timer.is_alive())
timer = threading.Timer(2, f)
timer.start()
print(timer)

'''
print("timer started")
if timer.is_alive():
    print("timer alive before")
else:
    print("timer dead before")
timer.cancel()
time.sleep(0.001)  # must sleep!
timer = threading.Timer(3, f)
timer.start()
#time.sleep(3.015)
if timer.is_alive():
    print("timer alive after")
else:
    print("timer dead after")
'''
