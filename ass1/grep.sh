#!/bin/sh
for i in "Sender_log.txt" "Receiver_log.txt"
do
    if [ $i == "Sender_log.txt" ]
    then
        echo "$i in $1(ms) timeout" >>report.txt
        tail -5 $i >>report.txt
        echo       >>report.txt
    elif [ $i == "Receiver_log.txt" ]
    then
        echo "$i in $1(ms) timeout" >>report.txt
        tail -3 $i >>report.txt
        echo       >>report.txt
    fi
done
