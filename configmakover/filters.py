from .utils import *
import lxml.etree

def applyFiltersToDict( data, filters ):
  '''Applys a set of given functions to all elements in a nested dict. The function called on each element is responsible for
     handling any errors.'''
  it = iterator(filters)
  for i in it:
    f = filters[i]
    if f is None:
      continue
    nargs = len(inspect.getargspec( f ).args)
    for item in dpath.util.search( data, "**", yielded=True, afilter=lambda x:True, separator='/' ):
      if nargs == 1:
        dpath.util.set( data, item[0], f(item[1]), separator='/' )
      if nargs == 2:
        dpath.util.set( data, item[0], f(item[1], item[0]), separator='/' )

  return data

def applyFiltersToDataTree( data, filters ):
  '''Applys a set of given functions to all elements in a DataTree. The function called on each element is responsible for
     handling any errors.'''
  it = iterator(filters)
  for i in it:
    f = filters[i]
    if f is None:
      continue
    nargs = len(inspect.getargspec( f ).args)
    for item in dpath.util.search( data.data, "**", yielded=True, afilter=lambda x:True, separator='/' ):
      if nargs == 1:
        dpath.util.set( data.data, item[0], f(item[1]), separator='/' )
      if nargs == 2:
        dpath.util.set( data.data, item[0], f(item[1], item[0]), separator='/' )
      if nargs == 3:
        dpath.util.set( data.data, item[0], f(item[1], item[0], data.spec), separator='/' )

  return data

def applyFiltersToDict( data, filters ):
  '''Applys a set of given functions to all elements in a nested dict. The function called on each element is responsible for
     handling any errors.'''
  it = iterator(filters)
  for i in it:
    f = filters[i]
    if f is None:
      continue
    nargs = len(inspect.getargspec( f ).args)
    for item in dpath.util.search( data, "**", yielded=True, afilter=lambda x:True, separator='/' ):
      if nargs == 1:
        dpath.util.set( data, item[0], f(item[1]), separator='/' )
      if nargs == 2:
        dpath.util.set( data, item[0], f(item[1], item[0]), separator='/' )

  return data


def applyFiltersToETree( data_tree, filters ):
  '''Apply filters to etree'''
  if not isinstance( filters, list ):
    filters = [filters]

  for e in data_tree.iter():
    if 'type' in e.attrib:
      e.attrib
    it = iterator(filters)
    if not it is None:
      for i in it:
        filter = filters[i]
        if filter is None:
          continue
        filter( e )




def isContainer( val ):
  return ( isinstance(val,Mapping) or isinstance(val,Sequence) ) and not isinstance(val,STR_TYPES)


def toNum( val ):
  '''Casts all data in a tree to numbers if possible'''
  if isContainer(val):
    return val

  if isinstance(val,lxml.etree._Element):
    if 'type' in val.attrib:
      val.attrib['type'] = 'float'
  else:
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
