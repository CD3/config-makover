import StringIO
import re
import pint, numpy, scipy.interpolate

class DataTable:
  '''Class that wraps a simple data table.'''

  ureg=pint.UnitRegistry()

  def __init__( self, filename = None, spec = dict()):
    self.filename = filename
    self.spec = spec
    self.data = None
    self.interp = None

    if not self.filename is None:
      self.load()

  def load(self, fn = None):
    if not fn is None:
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
    self.data = numpy.loadtxt( fh, unpack=True )

    self.interps = [ scipy.interpolate.interp1d( self.data[0], self.data[j] ) for j in range(1,len(self.data) ) ]

    return

  def loads(self, text):
    fh = StringIO.StringIO(text)
    self.loadfh(fh)

  def __call__(self,i,j=None):
    if j is None:
      j = i
      i = 0
    return self.data[j][i]

  def interp(self,x,j=0):
    pass

  def get(self,i,j=None,unit=None,default=None):
    if j is None:
      j = i
      i = 0

    units = ""
    if 'units' in self.spec:
      if j < len(self.data):
        units = self.spec['units'][j]
    q = self.ureg.Quantity( self(i,j), units )
    if unit:
      q.ito(unit)

    return q


  def __str__(self):
    text = ""
    for i in range(len(self.data)):
      for j in range(len(self.data[i])):
        text += str(self.data[i][j])
        text += " "
      text += "\n"
    return text


