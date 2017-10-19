#!/usr/bin/sh

for rate in {1..5}
do
    for mode in SHP SDP LLP
    do
        echo "================================="
        echo "$mode: $rate"
        ./RoutingPerformance.py PACKET $mode topology.txt workload.txt $rate | sed -n -e 4p -e 7,8p | cut -d: -f2 | tr -d ' '  
    done
done
