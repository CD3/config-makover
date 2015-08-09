import inspect
from collections import Mapping, Sequence, Container
import dpath.util
import tempita

STR_TYPES = (str,unicode)
def iterator( obj ):
  if isinstance( obj, Mapping ):
    return obj
  if isinstance( obj, Sequence) and not isinstance( obj, STR_TYPES ):
    return xrange( len( obj ) )
  return None

def dict2bunch( d ):
  '''Replaces all dict's in a data tree with with tempita.bunch's.'''
  it = iterator( d )
  if it:
    for i in it:
      d[i] = dict2bunch( d[i] )

  if isinstance( d, Mapping ):
    return tempita.bunch( **d )
  else:
    return d

class AttrDict(dict):
  '''A dict that allows attribute style access'''
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__


