#!/bin/bash

mkdir -p rawchats
mkdir -p convertedchats
mkdir -p analyzed

python downloader.py --outfile rawchats/tmp --username $1
./batch_convert.sh
python analyze.py --infolder convertedchats/ --outfolder analyzed/ --plot --msg --anonymize --stats --fromsender $1
