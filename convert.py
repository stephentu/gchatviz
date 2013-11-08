#!/usr/bin/env python2

# Convert downloaded messages into something useful

from message import message
import pickle
import sys
import re
from datetime import datetime as dt
from dateutil import parser as du_parser
from lxml import etree

NAMEPAT = re.compile(r'.*<(.+)>')
def extractemail_emailformat(text):
  m = NAMEPAT.match(text)
  if m:
    return m.group(1)
  return text

SUBPAT = re.compile(r'/.*')
def extractemail_gmailformat(text):
  # gmail adds a trailing slash, like a@b/gmail.XXYY sometimes. here we strip
  # off all the stuff after the /
  return SUBPAT.sub('', text)

if __name__ == '__main__':
  (_, infile, outfile) = sys.argv
  with open(infile, 'r') as infp:
    d = pickle.load(infp)
  msgs = []
  for m in d:
    if type(m) == dict:
      msg = message(
          extractemail_emailformat(m['from']),
          extractemail_emailformat(m['to']),
          du_parser.parse(m['date']),
          m['body'])
      msgs.append(msg)

    elif type(m) == str:
      conv = etree.fromstring(m)
      for msg in conv:
        fromuser = msg.attrib['from']
        touser = msg.attrib['to']

        bodynode = msg.findtext('{jabber:client}body')
        if bodynode is None:
          # some sort of archive message, ignore it
          continue

        ### XXX: hack
        body = bodynode.encode('utf-8')

        unixtime = int(msg.find('{google:timestamp}time').attrib['ms'])/1000.
        msg = message(
            extractemail_gmailformat(fromuser),
            extractemail_gmailformat(touser),
            dt.fromtimestamp(unixtime),
            body)
        msgs.append(msg)

    else:
      print >>sys.stderr, '[ERROR] bad message:', m

  print >>sys.stderr, '[INFO] processed %d messages' % (len(msgs))

  with open(outfile, 'w') as outfp:
    pickle.dump(msgs, outfp)
