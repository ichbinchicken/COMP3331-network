#!/usr/bin/python3

# Style: using camelCase

from sys import *
import re
import heapq
import math
import random

# constants
RELEASE = -1
OCCUPY = 1
VC = 0
VP = 1
TOTAL_REQ = 0
TOTAL_PAK = 1
SUCCESS_PAK = 2
BLOCKED_PAK = 3
TOTAL_HOP = 4
TOTAL_DELAY = 5
SUCCESS_CIR = 6


# node is char, index is integer
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
            #if e.cap > e.occupied and visited[e.to] == False:
            if visited[e.to] == False:
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

    # update capacity and return path
    path = []

    for i in range(len(route)):
        for e in graph.nodes[route[i]]:
            if i<len(route)-1 and e.to == route[i+1] \
                    or i > 0 and e.to == route[i-1]:
                if e.occupied < e.cap:
                    path.append(e)
                else:
                    # debugging
                    print(" BLOCKED: "+src+"-"+dest)

                    return []

    # update capacity
    updateCap(path, OCCUPY)

    # debugging
    #debug_path = [chr(i+65) for i in route]
    for i in range(len(route)):
        if i==0:
            print(chr(route[i]+65), end="")
        for e in graph.nodes[route[i]]:
            if i<len(route)-1 and e.to==route[i+1]:
                print("--%d/%d--%c" % (e.occupied, e.cap, chr(e.to+65)), end="")
    print()

    return path


def updateCap(path, change):
    #global graph
    # e.g. path = [e(AC),e(CA),e(CE),e(EC),e(EG),e(GE),e(GT),e(TG)]
    for edge in path:
        edge.occupied += change


def readWorkload():
    workload = []

    try:
        fw = open(argv[4], "r")
        for line in fw:
            # skip empty line or white spaces
            if len(line)==0 or line.isspace():
                continue
            line.rstrip()
            (start, src, dest, duration) = re.split(" ", line)
            startT = float(start)
            durationT = float(duration)
            workload.append((startT, src, dest, durationT))

    except IOError:
        print("argv[4]: File doesn't exist.")
        exit()

    return workload


def virtualCircuit(workload):
    # elements in connections: (endtime, path)
    connections = []

    for start, src, dest, duration in workload:

        while len(connections) > 0 and connections[0][0] <= start:
            _, path = heapq.heappop(connections)
            # free up capacity
            updateCap(path, RELEASE)

        newPath = dijkstra(index(src), index(dest))

        # if not blocked
        if newPath:
            heapq.heappush(connections, (start+duration, newPath))


def virtualPacket():
    global graph, stats
    requests = []
    workload = readWorkload()
    rate = int(argv[5])

    # add every packet into list
    for start, src, dest, duration in workload:
        numPackets = int(math.floor(duration*rate))
        interval = 1/rate
        startT = start
        for i in range(numPackets):
            if startT+interval > start+duration:
                stats[BLOCKED_PAK] += numPackets-i
                break
            requests.append((startT, src, dest, interval))
            startT += interval

    # sort list by start time
    # element in requests: (start, src, dest, duration)
    requests.sort(key=lambda packet:packet[0])
    virtualCircuit(requests)


def printStats(flag):
    global stats
    # TODO: need to confirm VP stats, whether per packet or per request
    print("total number of virtual connection requests: "+stats[TOTAL_REQ])
    print("total number of packets: "+stats[TOTAL_PAK])
    print("number of successfully routed packets: "+stats[SUCCESS_PAK])
    print("percentage of successfully routed packets: %.2f" % (stats[SUCCESS_PAK]/stats[TOTAL_PAK]))
    print("number of blocked packets: "+stats[BLOCKED_PAK])
    print("percentage of blocked packets %.2f" % (stats[BLOCKED_PAK]/stats[TOTAL_PAK]))

    ave_hops = ave_delay = -1
    if flag==VC:
        ave_hops = stats[TOTAL_HOP]/stats[SUCCESS_CIR]
        ave_delay = stats[TOTAL_DELAY]/stats[SUCCESS_CIR]
    elif flag==VP:
        ave_hops = stats[TOTAL_HOP]/stats[SUCCESS_PAK]
        ave_delay = stats[TOTAL_DELAY]/stats[SUCCESS_PAK]

    print("average number of hops per circuit: %.2f" % ave_hops)
    print("average cumulative propagation delay per circuit: %.2f" % ave_delay)


def main():
    global graph, stats
    stats = [0] * 7
    buildGraph()
    random.seed(42)
    if argv[1] == "CIRCUIT":
        virtualCircuit(readWorkload())
        printStats(VC)
    elif argv[1] == "PACKET":
        virtualPacket()
        printStats(VP)
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