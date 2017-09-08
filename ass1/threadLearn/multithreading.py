from threading import *
hash = {}
hash["sending"] = "sending"
hash[]
class MyThread(Thread):
    def __init__(self, func, args, name=''):
        Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
    def run(self):
        self.func(*self.args)

