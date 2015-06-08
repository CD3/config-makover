import dpath.util
import inspect

def iterator( obj ):
  if isinstance( obj, dict ):
    return obj
  if isinstance( obj, list ):
    return xrange( len( obj ) )
  return None

def applyFilters( data, filters ):
  '''Applys a set of given functions to all elements in a data tree. The function called on each element is responsible for
     handling any errors.'''
  it = iterator(filters)
  if not it:
    filters = [filters]

  it = iterator(filters)
  for i in it:
    filter = filters[i]
    nargs = len(inspect.getargspec( filter ).args)
    for item in dpath.util.search( data, "**", yielded=True, separator='.' ):
      if nargs == 1:
        dpath.util.set( data, item[0], filter(item[1]), separator='.' )
      if nargs == 2:
        dpath.util.set( data, item[0], filter(item[1], item[0]), separator='.' )

  return data


def toNum( val ):
  '''Casts all data in a tree to numbers if possible'''
  try:
    t = int
    if str(val).find('.') > -1:
      t = float
    # TODO: add complex support
      
    return t(str(val))
  except ValueError:
    return val

def toAttrDict( d ):
  '''Replaces all intances of dict() with AttrDict() in a data tree.'''
  it = iterator( d )
  if it:
    for i in it:
      d[i] = toAttrDict( d[i] )

  if isinstance( d, dict ):
    return AttrDict( d )
  else:
    return d

class AttrDict(dict):
  '''A dict that allows attribute style access'''
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__


