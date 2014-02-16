#!/bin/bash

mkdir -p rawchats
mkdir -p convertedchats
mkdir -p analyzed

python downloader.py --outfile rawchats/tmp
./batch_convert.sh
python analyze.py --infolder convertedchats/ --outfolder analyzed/ --plot --msg --hidemessages --stats
