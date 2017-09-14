#!/bin/sh
for i in "Sender_log50.txt" "Receiver_log50.txt" "Receiver_log200.txt" "Sender_log200.txt" "Sender_log800.txt" "Receiver_log800.txt"
do
    echo "tee"
    if egrep "Sender_log.*" $i 
    then
        echo "$i"
        tail -5 $i
        et=`cat "$i" | tail -10 | egrep rcv | egrep " A" | cut -c6-11`
        st=`cat "$i" | head -4 | egrep D | cut -c6-11`
        elapsed=`echo "$et - $st"|bc`
        echo "sender time: $elapsed" 
        echo      
    elif  egrep "Receiver_log.*" $i
    then
        echo "$i" 
        tail -3 $i 
        ret=`cat "$i" | tail -8 | egrep snd | egrep " A" | cut -c6-11`
        rst=`cat "$i" | head -4 | egrep D | cut -c6-11`
        relapsed=`echo "$ret - $rst"|bc`
        echo "receiver time: $relapsed"
        echo    
    fi
done
