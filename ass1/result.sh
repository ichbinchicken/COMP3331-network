for i in 50 200 800
do
    echo "$i ms"
    cat "Sender_log$i.txt" | tail -5
    cat "Receiver_log$i.txt" | tail -3

    et=`cat "Sender_log$i.txt" | tail -9 | egrep rcv | egrep " A" | cut -c6-11`
    echo $et
    st=`cat "Sender_log$i.txt" | head -4 | egrep D | cut -c6-11`
    echo $st
    elapsed=`echo "$et - $st"|bc`
    echo "sender time: $elapsed"

    ret=`cat "Receiver_log$i.txt" | tail -7 | egrep snd | egrep " A" | cut -c6-11`
    echo $ret
    rst=`cat "Receiver_log$i.txt" | head -4 | egrep D | cut -c6-11`
    echo $rst
    relapsed=`echo "$ret - $rst"|bc`
    echo "receiver time: $relapsed"

    echo "========"
done
