#!/bin/bash
source config.sh

mkdir -p rawchats convertedchats analyzed
$PYTHON downloader.py --outfile rawchats/tmp --username $1
FILES=rawchats/*
for f in $FILES
do
	echo "converting $f..." 
	$PYTHON convert.py $f convertedchats/${f##*/}
done
$PYTHON analyze.py --infolder convertedchats/ --outfolder testanalyzed/ --plot --msg --anonymize --stats --fromsender $1

