#!/bin/bash

mkdir rawchats
mkdir convertedchats
mkdir analyzed

python downloader.py --outfile rawchats/tmp
./batch_convert.sh
python analyze.py --infolder convertedchats/ --outfolder analyzed/ --plot --msg --hidemessages --stats
