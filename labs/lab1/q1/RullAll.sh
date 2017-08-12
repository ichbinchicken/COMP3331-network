#!/bin/bash
 while read -r line
do 
    ping -s 4 -c 10 $line>$line
done
