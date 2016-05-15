import StringIO
import re
import numpy

class DataFile:
  '''Class that wraps a simple data file.'''

  def __init__( self, filename = None, spec = dict()):
    self.filename = filename
    self.spec = spec
    self.data = None

  def load(self, fn = None):
    if fn:
      self.filename = fn

    with open(self.filename) as f:
      self.loadfh(f)

  def loadfh(self, fh):

    # scan for spec data first
    for line in fh:
      line = line.strip()
      if len(line) > 0 and line[0] == '#':
        tokens = line[1:].split()
        key = tokens[0]
        key = key.strip()
        key = key.strip(':')
        self.spec[ key ] = tokens[1:]

    # reset fh
    fh.seek(0,0)
    self.data = numpy.loadtxt( fh )

    return

  def loads(self, text):
    fh = StringIO.StringIO(text)
    self.loadfh(fh)

  def __getitem__(self,k):
    return self.data[k]

  def __call__(self,i,j=None):
    if j is None:
      j = i
      i = 0

    return self.data[i][j]


