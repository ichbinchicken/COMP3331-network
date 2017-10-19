#!/usr/bin/python3

# Style: using camelCase

from sys import *
import re
import heapq
import math
import random
import time

# constants
RELEASE = -1
OCCUPY = 1
VC = 0
VP = 1
TOTAL_REQ = 0
TOTAL_PAK = 1
SUCCESS_PAK = 2
SUCCESS_CIR = 3
TOTAL_HOP = 4
TOTAL_DELAY = 5


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
        # debugging
        # graph.printGraph()
    except IOError:
        print("argv[3]: File doesn't exist.")
        exit(1)

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
    global graph, stats
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
                    print("argv[2]: Invalid method")
                    exit(1)

                if dist[e.to] > newCost or (dist[e.to]==newCost and random.random()>0.5):
                    dist[e.to] = newCost
                    prev[e.to] = u

    # update capacity and return path
    p = dest
    while prev[p] != -1:
        route = [p] + route
        p = prev[p]
    if p != dest:
        route = [p] + route

    path = []

    for i in range(len(route)):
        for e in graph.nodes[route[i]]:
            if i<len(route)-1 and e.to == route[i+1] \
                    or i > 0 and e.to == route[i-1]:
                if e.occupied < e.cap:
                    path.append(e)
                else:
                    # debugging
                    # print(" BLOCKED: %c--%c" % (chr(src+65), chr(dest+65)))
                    return []

    # update capacity
    updateCap(path, OCCUPY)

    # write stats
    stats[TOTAL_HOP] += len(route)-1
    delay = 0
    for i in range(len(route)-1):
        for e in graph.nodes[route[i]]:
            if e.to == route[i+1]:
                stats[TOTAL_DELAY] += e.delay

    # debugging
    # for i in range(len(route)):
    #     if i==0:
    #         print(chr(route[i]+65), end="")
    #     for e in graph.nodes[route[i]]:
    #         if i<len(route)-1 and e.to==route[i+1]:
    #             print("--%d/%d--%c" % (e.occupied, e.cap, chr(e.to+65)), end="")
    # print()


    return path


def updateCap(path, change):
    #global graph
    # e.g. path = [e(AC),e(CA),e(CE),e(EC),e(EG),e(GE),e(GT),e(TG)]
    for edge in path:
        edge.occupied += change


def readWorkload():
    global stats, rate
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
            stats[TOTAL_PAK] += int(math.floor(durationT*rate))
    except IOError:
        print("argv[4]: File doesn't exist.")
        exit(1)

    stats[TOTAL_REQ] = len(workload)
    return workload


def virtualCircuit(workload, flag):
    global stats, rate
    # elements in connections: (endtime, path)
    connections = []

    for start, src, dest, duration in workload:
        if duration*rate < 1:
            continue
        numPackets = int(math.floor(duration*rate)) if flag==VC else 1

        while len(connections) > 0 and connections[0][0] <= start:
            _, path = heapq.heappop(connections)
            # free up capacity
            updateCap(path, RELEASE)

        newPath = dijkstra(index(src), index(dest))

        # if not blocked
        if newPath:
            heapq.heappush(connections, (start+duration, newPath))
            stats[SUCCESS_PAK] += numPackets
            if flag==VC:
                stats[SUCCESS_CIR] += 1


def virtualPacket():
    global stats, rate
    requests = []
    workload = readWorkload()

    # add every packet into list
    for start, src, dest, duration in workload:
        numPackets = int(math.floor(duration*rate))
        interval = 1/rate
        startT = start
        for i in range(numPackets):
            requests.append((startT, src, dest, interval))
            startT += interval

    # sort list by start time
    # element in requests: (start, src, dest, duration)
    requests.sort(key=lambda packet:packet[0])
    virtualCircuit(requests, VP)


def printStats(flag):
    global stats
    print("total number of virtual connection requests: %d" % stats[TOTAL_REQ])
    print("total number of packets: %d" % stats[TOTAL_PAK])
    print("number of successfully routed packets: %d" % stats[SUCCESS_PAK])
    print("percentage of successfully routed packets: %.2f" % (stats[SUCCESS_PAK]/stats[TOTAL_PAK]*100))

    blocked = stats[TOTAL_PAK] - stats[SUCCESS_PAK]
    print("number of blocked packets: %d" % blocked)
    print("percentage of blocked packets: %.2f" % (blocked/stats[TOTAL_PAK]*100))

    ave_hops = ave_delay = -1
    if flag==VC:
        ave_hops = stats[TOTAL_HOP]/stats[SUCCESS_CIR]
        ave_delay = stats[TOTAL_DELAY]/stats[SUCCESS_CIR]
    elif flag==VP:
        ave_hops = stats[TOTAL_HOP]/stats[SUCCESS_PAK]
        ave_delay = stats[TOTAL_DELAY]/stats[SUCCESS_PAK]

    # debugging
    # print("total hop %d, total delay %d, successful pak %d, successful cir %d" \
    #      % (stats[TOTAL_HOP], stats[TOTAL_DELAY], stats[SUCCESS_PAK], stats[SUCCESS_CIR]))

    print("average number of hops per circuit: %.2f" % ave_hops)
    print("average cumulative propagation delay per circuit: %.2f" % ave_delay)


def main():
    global graph, stats, rate
    stats = [0] * 6
    buildGraph()
    random.seed(time.time())

    if len(argv) < 6:
        print("error: Insufficient arguments")
        exit(1)
    else:
        rate = int(argv[5])

    if argv[1] == "CIRCUIT":
        virtualCircuit(readWorkload(), VC)
        printStats(VC)
    elif argv[1] == "PACKET":
        virtualPacket()
        printStats(VP)
    else:
        print("error: argv[1] wrong name")
        exit(1)

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
            if self.nodes[i]:
                print("%c: " % chr(i+65),end="")
                for e in self.nodes[i]:
                    print("%c(delay:%d,cap:%d) " % (chr(e.to+65), e.delay, e.cap), end="")
                print()
            i += 1

    # assuming the nodes are in alphabetical order and start from 'A'
    def realRange(self):
        count = 0
        for n in self.nodes:
            if n:
                count += 1
        return count


if __name__ == "__main__":
    main()