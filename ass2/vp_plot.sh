#!/usr/bin/sh


for mode in SHP SDP LLP
do
    echo "================================="
    echo "$mode"
    for rate in {1..5}
    do
        array=( $(./RoutingPerformance.py PACKET $mode topology.txt workload.txt $rate | sed -n -e 4p -e 7,8p | cut -d: -f2 | tr -d ' ') )
        SUCCESS[$rate-1]=${array[0]}
        HOP[$rate-1]=${array[1]}
        DELAY[$rate-1]=${array[2]}
    done
    echo "SUCCESS:"
    printf '%s\n' "${SUCCESS[@]}"
    echo "HOP:"
    printf '%s\n' "${HOP[@]}"
    echo "DELAY:"
    printf '%s\n' "${DELAY[@]}"
done
