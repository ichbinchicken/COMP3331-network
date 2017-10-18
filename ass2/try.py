#!/usr/bin/python3

# Style: using camelCase
from sys import *
import re
import heapq
import math
import random

# node is char of node
# index is integer index of node
def index(node):
    return ord(node)-ord('A')


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
def minDistance(dist, visited):
    global graph
    minDist = maxsize
    pos = -1
    for k in range(graph.realRange()):
        if dist[k] < minDist and visited[k] == False:
            minDist = dist[k]
            pos = k

    return pos


# return a list of edge from src to dest
# if failed return a empty list
def dijkstra(src, dest): # pass in index
    global graph
    route = []
    indexRange = graph.realRange()

    dist = [maxsize] * indexRange
    prev = [-1] * indexRange
    visited = [False] * indexRange

    dist[src] = 0

    while False in visited:
        u = minDistance(dist, visited)
        visited[u] = True
        for e in graph.nodes[u]:
            if e.cap > e.occupied and visited[e.to] == False:
                newCost = maxsize
                if argv[2] == "SHP":
                    newCost = dist[u]+1
                elif argv[2] == "SDP":
                    newCost = dist[u]+e.delay
                elif argv[2] == "LLP":
                    newCost = max(dist[u], e.occupied/e.cap)
                else:
                    print("argv[2]:Invalid method")
                    exit()

                if dist[e.to] > newCost or (dist[e.to]==newCost and random.random()>0.5):
                    dist[e.to] = newCost
                    prev[e.to] = u

    p = dest

    while p != -1:
        route = [p] + route
        p = prev[p]

    # debugging
    print(route)

    # update capacity and return path
    path = []

    for i in range(len(route)):
        for e in graph.nodes[route[i]]:
            if (i<len(route)-1 and e.to == route[i+1]) \
                    or (i > 0 and e.to == route[i-1]):
                if e.occupied < e.cap:
                    e.occupied += 1
                    path.append(e)
                else:
                    return []

    return path


def releaseCap(path):
    global graph
    # e.g. path = [e(AC),e(CA),e(CE),e(EC),e(EG),e(GE),e(GT),e(TG)]
    for edge in path:
        edge.occupied -= 1


def readWorkload():
    workload = []

    try:
        fw = open(argv[4], "r")
        for line in fw:
            line.rstrip()
            (start, src, dest, end) = re.split(" ", line)
            endT = float(end)
            startT = float(start)
            workload.append((startT, src, dest, endT))

    except IOError:
        print("argv[4]: File doesn't exist.")
        exit()

    return workload


def virtualCircuit(workload):
    connections = []

    for start, src, dest, end in workload:

        while len(connections) > 0 and connections[0][0] < start:
            _, path = heapq.heappop(connections)
            # free up capacity
            releaseCap(path)

        newPath = dijkstra(index(src), index(dest))

        # if not blocked
        if newPath:
            heapq.heappush(connections, (end, newPath))


def virtualPacket():
    global graph
    requests = []
    workload = readWorkload()
    rate = int(argv[5])

    # add every packet into list
    for start, src, dest, end in workload:
        duration = end-start
        numPackets = int(math.ceil(duration)*rate)
        interval = 1/rate
        startT = start
        for i in range(numPackets):
            endT = min(startT+interval, end)
            requests.append((startT, src, dest, endT))
            startT += interval

    # sort list by start time
    # element in requests: (start, src, dest, end)
    requests.sort(key=lambda packet:packet[0])
    virtualCircuit(requests)


def main():
    global graph
    buildGraph()
    random.seed(42)
    if argv[1] == "CIRCUIT":
        virtualCircuit(readWorkload())
    elif argv[1] == "PACKET":
        virtualPacket()
    else:
        print("error: argv[1] wrong name")
        exit()


class Edge:
    def __init__(self, to, delay, cap):
        self.delay = delay
        self.cap = cap
        self.to = index(to)  # vertex to (dest)
        self.occupied = 0


class Graph:
    def __init__(self):
        self.nodes = [[] for node in range(26)]
        #self.range = 0

    def addEdge(self, node, e):
        self.nodes[index(node)].append(e)

    def printGraph(self):
        i = 0
        while i < 26:
            if self.nodes[i]:
                print("%c: " % chr(i+65),end="")
                for e in self.nodes[i]:
                    print("%c(delay:%d,cap:%d) " % (chr(e.to+65), e.delay, e.cap), end="")

                print("")
            i += 1

    # assuming the nodes are in alphabetical order
    def realRange(self):
        count = 0
        for n in self.nodes:
            if n:
                count += 1
        return count


if __name__ == "__main__":
    main()