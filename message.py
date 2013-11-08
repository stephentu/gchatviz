class message(object):
  def __init__(self, fromuser, touser, date, message):
    self._fromuser = fromuser
    self._touser = touser
    self._date = date
    self._message = message

  def __str__(self):
    return '<from: %s, to: %s, date: %s, msg: %s>' % (self._fromuser, self._touser, self._date, self._message)
