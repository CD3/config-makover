import os, re
import __builtin__
import dpath
import pint

import DataTable

u = pint.UnitRegistry()
u.define( 'percent = 0.01 radian = %' )
# some convience aliases
u.define( 'dC = delta_degC' )
u.define( 'dF = delta_degF' )

DataTable = DataTable.DataTable
DataTable.ureg = u

def dpath_util_get(obj,path,separator='/'):
  # get rid of any separators at the beginning and end
  path = path.strip(separator)
  if separator in path:
    head,rest = path.split(separator,1)
    if isinstance( obj, list ):
      head = int(head)
    return dpath_util_get(obj[head],rest,separator)
  else:
    if isinstance( obj, list ):
      path = int(path)
    return obj[path]

def dpath_util_isglob(glob):
  return '*' in glob

dpath.util.get = dpath_util_get
dpath.util.isglob = dpath_util_isglob

def Q(x):
  return u.Quantity(x)

def mag(x):
  if isinstance(x,pint.quantity._Quantity):
    return x.magnitude
  return x

class DataTree(object):

  ureg = u
  '''Simple wrapper for nested dicts that allows accessing dict elements with paths like a filesystem.'''
  def __init__(self, d = dict(), p = '/', s = dict()):
    self.root = p     # the path to this trees root element
    self.data = d     # the dictionary that this tree presents a view of
    self.spec = s     # specification data (meta data) for the elements in the tree

  def _join(self,*args):
    return os.path.normpath( os.path.join( *args ) )

  def _abspath(self,p):
    if p[0] == '/':
      path = p
    else:
      path = self._join( self.root, p )

    return os.path.normpath( path )

  def _spec_entry( self, path, entry):
    '''Return an element from the spec. Returns None if no type exists in the spec.'''
    try:
      return dpath.util.get( self.spec, self._join( path, entry) )
    except:
      return None

  def _type( self, path ):
    return self._spec_entry(path,'type')

  def _unit( self, path ):
    return self._spec_entry(path,'unit')

  def _default( self, path ):
    return self._spec_entry(path,'default')

  def _totype( self, val, typelist ):
    if typelist == 'raw' or typelist is None:
      return val

    if isinstance(typelist, (str,unicode) ):
      types = typelist.split('|')
    else:
      types = [typelist]

    for t in types:
      if isinstance(t, (str,unicode)):
        t = eval(t)
      val = t(val)

    return val

  def _tounit( self, val, unit ):
    try:
      q = self.ureg.Quantity(val)
      if q.units == u.dimensionless:
        q = self.ureg.Quantity(str(val) + " " + str(unit))
      return q.to(unit)
    except:
      return val

  def _getdefault( self, path ):
    '''Get default value for a given path.'''

    # first, see if a default value exists for the path.
    default = self._default(path)
    if not default is None:
      return default
    
    return None

  def _get_paths(self, data, glob = '**', afilter = lambda x: True):
    return [ x[0] for x in dpath.util.search( data, self._abspath(glob), afilter=lambda x:True, yielded=True ) ]


  def __getitem__(self,k):
    if isinstance(k,tuple):
      return self.get(k[0],k[1])
    else:
      return self.get(k)

  def __setitem__(self,k,v):
    return self.set(k,v)

  def has(self,k):
    '''Returns true if data tree contains key k.'''
    return len( self.get_paths(k) ) > 0

  def get(self,p,type=None,unit=None,default=None):
    def first(*args):
      for a in args:
        if not a is None:
          return a

    path = self._abspath(p)
    try:
      val = dpath.util.get( self.data, path )
    except KeyError as e:
      val = first( default, self._getdefault( path ) )
      if val is None:
        raise e


    val = self._tounit( val, first( unit, self._unit( path ) ) )
    val = self._totype( val, first( type, self._type( path ) ) )

    return val

  def set(self,p,v):
    return dpath.util.new( self.data, self._abspath(p), v )

  def get_node(self,p):
    '''Return a DataTree rooted at the path p.'''
    return DataTree( self.data, self._abspath( p )+'/' )

  def add_spec(self,path,speckey,val):
    '''Add an entry to the spec. The data tree is searched for keys matching path. If any keys
    are found, an entry in the spec is added under each matched key..
    '''

    keygen = self._join

    # if path is a glob, create spec entries for each key that matches the glob
    if dpath.util.isglob(path):
      for x in dpath.util.search( self.data, self._abspath(path), afilter=lambda x:True, yielded=True ):
        self.set_spec( keygen(x[0],speckey), val )
    else:
      # otherwise, just add it directly
       self.set_spec( keygen(path,speckey), val )

  def set_spec(self,glob,v):
    dpath.util.new( self.spec, glob, v )

  def get_spec(self,path,k=None):
    try:
      if k:
        path = self._join( path, k )
      return dpath.util.get( self.spec, path )
    except:
      return None

  def get_paths(self, glob = '**', afilter = lambda x: True):
    return self._get_paths( self.data, glob, afilter )

  def get_spec_paths(self, glob = '**', afilter = lambda x: True):
    return self._get_paths( self.spec, glob, afilter )



  # legacy functions
  new_spec = add_spec
        



