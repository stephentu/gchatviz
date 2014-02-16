#!/bin/bash

FILES=rawchats/*

for f in $FILES
do
	echo "converting $f..." 
	python convert.py $f convertedchats/${f##*/}
done