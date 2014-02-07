#!/usr/bin/env python2

# Download chats from gmail

import sys
import imaplib
import email
import argparse
import pickle

def error(msg, exitcode=1):
  print >>sys.stderr, '[ERROR]', msg
  if exitcode is not None:
    sys.exit(exitcode)

def info(msg):
  print >>sys.stderr, '[INFO]', msg

def saveresults(results, outfp):
  pickle.dump(results, outfp)
  outfp.flush()

if __name__ == '__main__':
  p = argparse.ArgumentParser()
  p.add_argument('--username', required=True)
  p.add_argument('--password', required=True) # XXX: don't take from command line
  p.add_argument('--target-username', required=True)
  p.add_argument('--outfile', required=True)
  p.add_argument('--limit', type=int, default=100)
  p.add_argument('--offset', type=int, default=0)
  args = p.parse_args()

  if args.limit <= 0:
    error("--limit must be > 0")

  if args.offset < 0:
    error('--offset must be >= 0') # XXX: support -N offsets

  with open(args.outfile, 'w') as testfp:
    # just testing to make sure we can open
    pass

  mail = imaplib.IMAP4_SSL('imap.gmail.com')
  mail.login(args.username, args.password)
  stat, msg = mail.select('[Gmail]/Chats', True)
  if stat != 'OK':
    error("Could not open chats folder: " + msg)

  # get all mail
  stat, msg = mail.search(None, "ALL")
  if stat != 'OK':
    error("Could not search folder for target user: " + msg)
  # stat, msg = mail.search(None, 'FROM', '"%s"' % (args.target_username))
  # if stat != 'OK':
  #   error("Could not search folder for target user: " + msg)
  # stat, msg1 = mail.search(None, 'TO', '"%s"' % (args.target_username))
  # if stat != 'OK':
  #   error("Could not search folder for target user: " + msg)

  #ids = msg[0].split() + msg1[0].split() # space delimited ids
  ids = msg[0].split()
  total_msgs = len(ids)
  info('Found %d conversations, but limiting to [%d, %d)' % (
    total_msgs, args.offset, args.offset + args.limit))
  ids = ids[args.offset : args.offset + args.limit]

  chatmsgs = []
  completed = 0
  for idx in ids:
    # XXX: do in parallel
    stat, fetchmsg = mail.fetch(idx, '(RFC822)')
    if stat != 'OK':
      with open(args.outfile, 'w') as outfp:
        saveresults(chatmsgs, outfp)
      error('Could not fetch email with ID %s: %s' % (idx, fetchmsg))
    msg = email.message_from_string(fetchmsg[0][1])

    # gmail exports either text or XML
    if msg.get_content_maintype() == 'text':
      # for this case, we need to use the e-mail metadata for context
      dictmsg = {
          'from' : msg['From'],
          'to' : msg['To'],
          'date' : msg['Date'],
          'body' : msg.get_payload(decode=True)
      }
      chatmsgs.append(dictmsg)

    else:
      # in this case, we'll simply save the XML as a string.  the XML itself
      # contains all the info we need to reconstruct messages

      assert msg.get_content_maintype() == 'multipart', 'bad msg maintype'

      payload = msg.get_payload(0)

      # assert we have XML
      assert payload.get_content_type() == 'text/xml', 'bad message content type'

      xmlmsg = payload.get_payload(decode=True)
      chatmsgs.append(xmlmsg)

    completed += 1
    if (completed % 1000) == 0:
      info('Finished downloading %d/%d message' % (completed, len(ids)))

  with open(args.outfile, 'w') as outfp:
    saveresults(chatmsgs, outfp)
