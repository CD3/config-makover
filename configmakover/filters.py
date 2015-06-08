from .utils import *

def applyFilters( data, filters ):
  '''Applys a set of given functions to all elements in a data tree. The function called on each element is responsible for
     handling any errors.'''
  it = iterator(filters)
  if not it:
    filters = [filters]

  it = iterator(filters)
  for i in it:
    filter = filters[i]
    if filter is None:
      continue
    nargs = len(inspect.getargspec( filter ).args)
    for item in dpath.util.search( data, "**", yielded=True, separator='.' ):
      if nargs == 1:
        dpath.util.set( data, item[0], filter(item[1]), separator='.' )
      if nargs == 2:
        dpath.util.set( data, item[0], filter(item[1], item[0]), separator='.' )

  return data


def isContainer( val ):
  return isinstance(val,dict) or isinstance(val,list)


def toNum( val ):
  '''Casts all data in a tree to numbers if possible'''
  if isContainer(val):
    return val

  try:
    t = int
    if str(val).find('.') > -1:
      t = float
    # TODO: add complex support
      
    return t(str(val))
  except ValueError:
    return val

def expand_list( val ):
  '''Expands a string of comma separated values into a list instance.'''
  if isContainer(val):
    return val

  try:
    if isinstance(val, unicode):
      val = str(val)

    if isinstance(val, str):
      if val.find(',') > -1:
        val = val.strip().split(',')
    else:
      val = float(val)

  except:
    return val
  
  return val
