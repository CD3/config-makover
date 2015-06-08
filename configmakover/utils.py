import dpath.util

def iterator( obj ):
  if isinstance( obj, dict ):
    return obj
  if isinstance( obj, list ):
    return xrange( len( obj ) )
  return None

def toNums( data ):
  '''Casts all data in a tree to numbers if possible'''
  for item in dpath.util.search( data, "**", yielded=True ):
    try:
      t = int
      if str(item[1]).find('.') > -1:
        t = float

      # TODO: add complex support
        
      dpath.util.set( data, item[0], t(str(item[1])) )
    except ValueError:
      pass

  return data

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


