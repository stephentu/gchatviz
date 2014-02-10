#!/usr/bin/env python

from message import message
import argparse
import pickle
import sys
import pytz
import os
import errno
import itertools as it
import numpy
import csv
from datetime import datetime as dt
from datetime import time as dtime

from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, \
    HourLocator, MinuteLocator, DateFormatter

def mkdirp(path):
  # worst idiom ever
  try:
    os.makedirs(path)
  except OSError as exc:
    if exc.errno == errno.EEXIST:
      pass
    else:
      raise

def argmax(seq, keyfn=lambda x: x):
  best, best_value = seq[0], keyfn(seq[0])
  for e in seq[1:]:
    if keyfn(e) > best_value:
      best, best_value = e, keyfn(e)
  return best

def groupby(dates):
  """
  given a list of ordered objects, returns a list of [(obj, count)],
  in ascending object order
  """
  m = {}
  for d in dates:
    m[d] = m.get(d, 0) + 1
  return sorted(m.iteritems())

def write_tocsv(messages, outfile):
  with open(outfile, "w") as out:
    writer = csv.writer(out)
    writer.writerow(["sender","message","datetime"])
    for m in messages:
      row = [m._fromuser, m._message.replace('\n', ' '), clean_date(str(m._date))]
      writer.writerow(row)

def clean_date(date):
  without_microseconds = date.split('.')[0]
  time = without_microseconds.split(" ")[1]
  if "-" in time:
    to_remove = time.split("-")[1]
    return without_microseconds.replace(to_remove, '')
  else:
    return without_microseconds

def getdatestats(messages):
  dateinfo = [m._date.date() for m in messages]
  stats = {}
  stats["chatsperday"] = avgchatsperday(dates)

def avgchatsperday(dates):
  ts = groupby(dates)
  return numpy.average([x[1] for x in ts])

def plot(messages, infile, outfolder):
      # count messages sent by user
  msg_counts = {}
  word_counts = {}
  for m in messages:
    nwords = len(m._message.split())
    msg_counts[m._fromuser] = msg_counts.get(m._fromuser, 0) + 1
    word_counts[m._fromuser] = word_counts.get(m._fromuser, 0) + nwords


  dateinfo = [m._date.date() for m in messages]
  fig = plotbydate(dateinfo)
  fig.savefig(os.path.join(outfolder, infile + '_activity-date.pdf'))

  fig = plotbyavgtime([m._date for m in messages])
  fig.savefig(os.path.join(outfolder, infile + '_activity-time.pdf'))

def plotbydate(dates):
  ts = groupby(dates)
  print argmax(ts, lambda x: x[1])

  years = YearLocator()
  months = MonthLocator()
  yearsFmt = DateFormatter('%Y')

  fig, ax = plt.subplots()
  ax.plot_date([t[0] for t in ts], [t[1] for t in ts], '-')

  # format the ticks
  ax.xaxis.set_major_locator(years)
  ax.xaxis.set_major_formatter(yearsFmt)
  ax.xaxis.set_minor_locator(months)
  ax.autoscale_view()

  # format the coords message box
  ax.fmt_xdata = DateFormatter('%Y-%m-%d')
  ax.grid(True)
  fig.autofmt_xdate()

  ax.set_ylabel('Messages/Day')
  ax.set_title('GChat Activity')

  return fig

def buckettime(t):
  return t.replace(minute=int(t.minute / 10.0)*10, second=0, microsecond=0)

def plotbyavgtime(datetimes):
  ndays = len(set(d.date() for d in datetimes))

  # bucket each time object
  datetimes = map(buckettime, datetimes)

  counts = {}
  for k, g in it.groupby(datetimes):
    mykey = k.time()
    mysum, mycnt = counts.get(mykey, (0,0))
    counts[mykey] = (mysum + len(list(g)), mycnt + 1)

  ts = []
  # plot can only handle date objects, not time objects
  hack = dt.now()
  for h in xrange(24):
    for m in xrange(0, 60, 10):
      t = dtime(h, m)
      mysum, mycnt = counts.get(t, (0,0))
      assert mycnt <= ndays
      ts.append((dt.combine(hack, t), mysum / float(ndays)))

  print argmax(ts, lambda x: x[1])

  timefmt = DateFormatter('%I:%M%p')

  fig, ax = plt.subplots()
  ax.plot([t[0] for t in ts], [t[1] for t in ts], '-')

  # format the ticks
  ax.xaxis.set_major_locator(HourLocator())
  ax.xaxis.set_major_formatter(timefmt)
  ax.xaxis.set_minor_locator(MinuteLocator(interval=10))
  ax.autoscale_view()

  # format the coords message box
  ax.fmt_xdata = DateFormatter('%I:%M%p')
  ax.grid(True)
  fig.autofmt_xdate()

  ax.set_ylabel('avg msgs/day at time')
  ax.set_title('GChat Activity Breakdown by Time of Day')

  return fig

if __name__ == '__main__':
  p = argparse.ArgumentParser()
  p.add_argument('--infile', required=True)
  p.add_argument('--outfolder', required=True)
  p.add_argument('--plot', action='store_true')
  p.add_argument('--msg', action='store_true')
  p.add_argument('--stats', action='store_true')
  args = p.parse_args()

  mkdirp(args.outfolder)

  with open(args.infile, 'r') as infp:
    d = pickle.load(infp)

  # XXX: hacky-- add timezone info
  tz = pytz.timezone('US/Pacific')
  for idx in xrange(len(d)):
    if d[idx]._date.tzinfo is None:
      d[idx]._date = d[idx]._date.replace(tzinfo=tz)

  # sort by time
  messages = sorted(d, key=lambda x: x._date)

  if args.msg:
    print "processing message data..."
    write_tocsv(d, os.path.join(args.outfolder, args.infile.split("/")[1] + "_messagedata.csv"))

  if args.plot:
    print "plotting..."
    plot(messages, args.infile, args.outfolder)

  if args.stats:
    print "getting statistics..."
    getdatestats(messages)
  # write to text file
  #with open(outfile, 'w') as outfp:
  #  for m in d:
  #    print >>outfp, '%s -> %s (%s): %s' % (m._fromuser, m._touser, m._date.strftime('%x %X'), m._message)
