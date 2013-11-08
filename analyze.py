#!/usr/bin/env python

from message import message
import pickle
import sys
import pytz
import os
import errno

from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter

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

def aggregate_dates(dates):
  """
  given a list of dates, returns a list of [(date, count)],
  in ascending order
  """
  m = {}
  for d in dates:
    m[d] = m.get(d, 0) + 1
  return sorted(m.iteritems())

if __name__ == '__main__':
  (_, infile, outfolder) = sys.argv
  mkdirp(outfolder)

  with open(infile, 'r') as infp:
    d = pickle.load(infp)

  # XXX: hacky-- add timezone info
  tz = pytz.timezone('US/Pacific')
  for idx in xrange(len(d)):
    if d[idx]._date.tzinfo is None:
      d[idx]._date = d[idx]._date.replace(tzinfo=tz)

  # sort by time
  d = sorted(d, key=lambda x: x._date)

  # count messages sent by user
  msg_counts = {}
  word_counts = {}
  for m in d:
    nwords = len(m._message.split())
    msg_counts[m._fromuser] = msg_counts.get(m._fromuser, 0) + 1
    word_counts[m._fromuser] = word_counts.get(m._fromuser, 0) + nwords

  print msg_counts
  print word_counts

  ts = aggregate_dates([m._date.date() for m in d])
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

  #plt.show()
  plt.savefig(os.path.join(outfolder, 'activity.pdf'))

  # write to text file
  #with open(outfile, 'w') as outfp:
  #  for m in d:
  #    print >>outfp, '%s -> %s (%s): %s' % (m._fromuser, m._touser, m._date.strftime('%x %X'), m._message)
