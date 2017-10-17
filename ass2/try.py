# Style: using camelCase
from sys import *
import re
import heapq
import sys

# node is char of node
# index is integer index of node
def index(node):
    return ord(node)-ord('A')

class Edge:
    def __init__(self, to, delay, cap):
        self.delay = delay
        self.cap = cap
        self.to = index(to)  # vertex to (dest)
        self.occupied = 0


class Graph:
    def __init__(self):
        self.nodes = [[] for node in range(26)]

    def addEdge(self, node, e):
        self.nodes[index(node)].append(e)

    def printGraph(self):
        i = 0
        while i < 26:
            if self.nodes[i] != []:
                print("%c: " % chr(i+65),end="")
                for e in self.nodes[i]:
                    print("%c(delay:%d,cap:%d) " % (chr(e.to+65), e.delay, e.cap), end="")
                print("")
            i += 1

    def realRange(self):
        count = 0
        for n in self.nodes:
            if n != []:
                count += 1
        return count


def buildGraph():
    global graph
    graph = Graph()
    try:
        ft = open(argv[3],"r")
        for line in ft:
            line.rstrip()
            (node, to, delay, cap) = re.split(" ", line)
            graph.addEdge(node, Edge(to, int(delay), int(cap)))
            graph.addEdge(to, Edge(node, int(delay), int(cap)))
        graph.printGraph()
    except IOError:
        print("argv[3]: File doesn't exist.")
        exit()

# find an index which has the minimum distance among vertices and not in route[]
def miniDistance(dist, visited):
    global graph
    minDist = sys.maxsize
    for k in range(graph.realRange()):
        if dist[k] < minDist and visited[k] == False:
            minDist = dist[k]
            pos = k
    return pos


def dijkstra(src, dest): # pass in index
    global graph
    # return a list of edge from src to dest
    # if failed return a empty list
    route = [src]
    for i in range(graph.realRange()):
            dist = [sys.maxsize] * i
    for j in range(graph.realRange()):
            visited = [False] * j
    dist[src] = 0
    for n in range(graph.realRange()):
        u = miniDistance(dist, visited)
        visited[u] = True
        for e in graph.nodes[u]:
            


def updateCap(path):
    global graph
    # e.g. path = [e(AC),e(CA),e(CE),e(EC),e(EG),e(GE),e(GT),e(TG)]
    for edge in path:
        edge.occupied -= 1

def virtualCircuit():
    global graph
    try:
        fw = open(argv[4], "r")
        hqueue = []
        for line in fw:
            line.rstrip()
            (startTime, src, dest, endTime) = re.split(" ", line)
            endTime = float(endTime)
            startTime = float(startTime)
            while len(hqueue) > 0 and hqueue[0][0] < startTime:
                _, path = heapq.heappop(hqueue)
                # update capacity
                updateCap(path)
            newPath = dijkstra(index(src), index(dest))
            # if not blocked
            if newPath != []:
                heapq.heappush(hqueue, (endTime, newPath))
    except IOError:
        print("argv[4]: File doesn't exist.")
        exit()

def virtualPacket():
    #TODO


def main():
    global graph
    buildGraph()
    if argv[1] == "CIRCUIT":
        virtualCircuit()
    elif argv[1] == "PACKET":
        virtualPacket()
    else:
        print("error: argv[1] wrong name")
        exit()


if __name__ == "__main__":
    main()