#!/usr/bin/env python

from message import message
import pickle
import sys
import pytz

if __name__ == '__main__':
  (_, infile, outfile) = sys.argv
  with open(infile, 'r') as infp:
    d = pickle.load(infp)

  # XXX: hacky-- add timezone info
  tz = pytz.timezone('US/Pacific')
  for idx in xrange(len(d)):
    if d[idx]._date.tzinfo is None:
      d[idx]._date = d[idx]._date.replace(tzinfo=tz)

  # sort by time
  d = sorted(d, key=lambda x: x._date)

  with open(outfile, 'w') as outfp:
    for m in d:
      print >>outfp, '%s -> %s (%s): %s' % (m._fromuser, m._touser, m._date.strftime('%x %X'), m._message)
