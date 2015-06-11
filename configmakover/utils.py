import dpath.util
import inspect
from collections import Mapping, Sequence, Container

STR_TYPES = (str,unicode)
def iterator( obj ):
  if isinstance( obj, Mapping ):
    return obj
  if isinstance( obj, Sequence) and not isinstance( obj, STR_TYPES ):
    return xrange( len( obj ) )
  return None

def toAttrDict( d ):
  '''Replaces all intances of dict() with AttrDict() in a data tree.'''
  it = iterator( d )
  if it:
    for i in it:
      d[i] = toAttrDict( d[i] )

  if isinstance( d, Mapping ):
    return AttrDict( d )
  else:
    return d

class AttrDict(dict):
  '''A dict that allows attribute style access'''
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__


