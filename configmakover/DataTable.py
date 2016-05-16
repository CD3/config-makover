import StringIO
import re
import pint, numpy, scipy.interpolate

class DataTable:
  '''Class that wraps a simple data table.'''

  ureg=pint.UnitRegistry()

  def __init__( self, filename = None, spec = dict()):
    self._filename = filename
    self._spec = spec
    self._data = None
    self._interp = None

    if not self._filename is None:
      self.load()

  def __getstate__(self):
    '''Add pickle support.'''

    return { 'filename' : self._filename
           , 'spec' : self._spec
           , 'data' : self._data
           }

  def __setstate__(self,state):
    '''Add pickle support.'''

    self._filename = state['filename']
    self._spec = state['spec']
    self._data = state['data']
    self._setup_interp()


  def load(self, fn = None):
    if not fn is None:
      self._filename = fn

    with open(self._filename) as f:
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
        self._spec[ key ] = tokens[1:]

    # reset fh
    fh.seek(0,0)
    self._data = numpy.loadtxt( fh, unpack=True )
    self._setup_interp()


    return

  def loads(self, text):
    fh = StringIO.StringIO(text)
    self.loadfh(fh)

  def _setup_interp(self):
    self._interp = [ scipy.interpolate.interp1d( self._data[0], self._data[j] ) for j in range(1,len(self._data) ) ]
    return


  def _get_units(self,col):
    units = ""
    if 'units' in self._spec:
      if col < len(self._data):
        units = self._spec['units'][col]
    return units

  def _make_Q(self,v,col):
    '''Return a Quantity with units determined by the column number.'''

    q = self.ureg.Quantity( v, self._get_units(col) )

    return q

  def __call__(self,i,j=None):
    if j is None:
      j = i
      i = 0
    return self._data[j][i]

  def get(self,i,j=None,unit=None,default=None):
    '''Return a quantity from the table. This will return a quantity with units.
       If you just want the value of the quantity, use __call__.'''
    if j is None:
      j = i
      i = 0

    v = self(i,j)
    q = self._make_Q(v, j)
    if unit:
      q.ito(unit)

    return q

  def interp(self,x,j=None):
    '''Return an interpolated value from the table.'''
    if j is None:
      j = 0

    v = self._interp[j-1]( x )
    return v

  def iget(self,x,j=None,unit=None):
    '''Return an interpolated quantity from the table.'''
    if j is None:
      j = 1

    if not isinstance(x,pint.quantity._Quantity):
      x = self._make_Q(x,0)

    x = x.to( self._get_units(0) )

    v = self.interp(x,j)
    q = self._make_Q(v, j)
    if unit:
      q.ito(unit)

    return q


  def __str__(self):
    text = ""
    for i in range(len(self._data)):
      for j in range(len(self._data[i])):
        text += str(self._data[i][j])
        text += " "
      text += "\n"
    return text


