import os
import dpath
import pint
import __builtin__

u = pint.UnitRegistry()

def Q(x):
  return u.Quantity(x)

def mag(x):
  if isinstance(x,pint.quantity._Quantity):
    return x.magnitude
  return x


class DataTree(object):
  '''Simple wrapper for nested dicts that allows accessing dict elements with paths like a filesystem.'''
  def __init__(self, d = dict(), p = '/', s = dict()):
    self.root = p
    self.data = d
    self.spec = s

  def _join(self,*args):
    return os.path.normpath( os.path.join( *args ) )

  def _abspath(self,p):
    if p[0] == '/':
      path = p
    else:
      path = self._join( self.root, p )

    return os.path.normpath( path )

  def __getitem__(self,k):
    if isinstance(k,tuple):
      return self.get(k[0],k[1])
    else:
      return self.get(k)

  def __setitem__(self,k,v):
    return self.set(k,v)

  def _type( self, path ):
    '''Return the type spec for a path. Returns None if no type exists in the spec.'''
    try:
      return dpath.util.get( self.spec, self._join( path, 'type' ) )
    except:
      return None

  def _unit( self, path ):
    '''Return the type spec for a path. Returns None if no type exists in the spec.'''
    try:
      return dpath.util.get( self.spec, self._join( path, 'unit' ) )
    except:
      return None

  def _totype( self, val, typelist ):
    if typelist == 'raw' or typelist is None:
      return val

    types = typelist.split('|')
    for t in types:
      if isinstance(t, (str,unicode)):
        t = eval(t)
      val = t(val)

    return val

  def _tounit( self, val, unit ):
    try:
      return Q(val).to(unit)
    except:
      return val


  def has(self,k):
    '''Returns true if data tree contains key k.'''
    return len( self.get_paths(k) ) > 0


  def get(self,p,type=None,unit=None):
    def first(*args):
      for a in args:
        if not a is None:
          return a

    path = self._abspath(p)
    val = dpath.util.get( self.data, path )

    val = self._tounit( val, first( unit, self._unit( path ) ) )
    val = self._totype( val, first( type, self._type( path ) ) )

    return val

  def set(self,p,v):
    return dpath.util.new( self.data, self._abspath(p), v )

  def get_node(self,p):
    '''Return a DataTree rooted at the path p.'''
    return DataTree( self.data, self._abspath( p )+'/' )

  def set_spec(self,glob,v):
    dpath.util.new( self.spec, glob, v )

  def new_spec(self,glob,k,v):
    for x in dpath.util.search( self.data, self._abspath(glob), afilter=lambda x:True, yielded=True ):
      self.set_spec( self._join(x[0],k), v )

  def get_spec(self,path,k=None):
    try:
      if k:
        k = self._join( path, k )
      return dpath.util.get( self.spec, k )
    except:
      return None


  def get_paths(self, glob = '**', afilter = lambda x: True):
    return [ x[0] for x in dpath.util.search( self.data, self._abspath(glob), afilter=lambda x:True, yielded=True ) ]


