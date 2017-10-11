class Node:
    def __init__(self, val, delay, cap):
        self.val = val
        self.delay = delay
        self.cap = cap
        self.next = None

    def getVal(self):
        return self.val

    def getNext(self):
        return self.next

    def getDelay(self):
        return self.delay

    def getCap(self):
        return self.cap

    def setNext(self,next):
        self.next = next


nodeA = Node('A', 1, 2)
nodeB = Node('B', 3, 4)
nodeC = Node('C', 5, 6)
graph = [nodeA, nodeB, nodeC]



