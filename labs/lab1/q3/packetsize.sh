#!/bin/bash

for size in 50 250 500 750 1000 1250 1500
do
    egrep "ttl" $1-p$size | cut -d' ' -f8 | cut -c6- > $1$size.csv
done

