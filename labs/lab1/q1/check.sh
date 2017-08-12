#!/bin/bash

while read -r line
do
    echo "$line:"
    #egrep packets $line
    recvd="$(egrep packets $line | cut -d, -f2 | cut -c2-3)"
    #echo $recvd
    if [ "$recvd" = "10" ]
    then
		echo "reachable"
    else
       echo "unreachable"
    fi
done
