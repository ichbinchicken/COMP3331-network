#!/usr/bin/python3

# Style: using camelCase
from sys import *
import re
import heapq
import math

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
def miniDistance(dist, visited):
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
    prev = [maxsize] * indexRange
    visited = [False] * indexRange

    dist[src] = 0

    for n in range(indexRange):
        u = miniDistance(dist, visited)
        visited[u] = True
        for e in graph.nodes[u]:
            if (e.cap - e.occupied) > 0 and visited[e.to] == False:
                if argv[2] == "SHP":
                    if dist[e.to] > dist[u] + 1:
                        dist[e.to] = dist[u] + 1
                        prev[e.to] = u
                elif argv[2] == "SDP":
                    if dist[e.to] > dist[u] + e.delay:
                        dist[e.to] = dist[u] + e.delay
                        prev[e.to] = u
                elif argv[2] == "LLP":
                    ratio = e.occupied/e.cap
                    dist[e.to] = ratio
                    prev[e.to] = u
                else:
                    print("argv[2]:Invalid method")
                    exit()
    p = dest

    while p != src:
        route = [p] + route
        p = prev[p]

    # debugging
    print(route)
    # update capacity
    # return
    path = []
    i = 0

    while i < len(route):
        j = 0
        while j < len(graph.nodes[route[i]]):
            e = graph.nodes[route[i]][j]
            if e.to == route[i+1]:
                if (e.cap - e.occupied) > 0:
                    e.occupied += 1
                    path.append(e)
                else:
                    return []
            j += 1
        i += 1
    return path


def updateCap(path):
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


def virtualCircuit():
    global graph
    requests = []
    workload = readWorkload()

    for start, src, dest, end in workload:

        while len(requests) > 0 and requests[0][0] < start:
            _, path = heapq.heappop(requests)
            # update capacity
            updateCap(path)

        newPath = dijkstra(index(src), index(dest))

        # if not blocked
        if newPath != []:
            heapq.heappush(requests, (end, newPath))


def virtualPacket():
    global graph
    requests = []
    workload = readWorkload()
    rate = int(argv[5])

    # add every packet into list
    for start, src, dest, end in workload:
        duration = end-start
        numPackets = math.ceil(duration/rate)

    # sort list by start time
    requests.sort()


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