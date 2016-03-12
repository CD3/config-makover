import inspect, re, os
from collections import Mapping, Sequence, Container
import dpath.util
import tempita
import lxml.etree

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

class ETWrap:
  '''Lightweight wrapper class for accessing data in ElementTree and Element.'''

  parent_regex = re.compile('_up')
  index_regex  = re.compile('_([0-9]+)')
  def __init__( self, element = None ):
    self.e = element

  def __getattr__( self, key ):
    # see if special key for parent was given
    if ETWrap.parent_regex.match( key ):
      return ETWrap(self.e.getparent())

    # first, try to find the element we are being asked for.
    # we will decide what we should return after we find it.

    e = None

    # look for an element with the tag
    if e is None:
      e = self.e.find(key)

    # see if special key for index was given
    if e is None:
      m = ETWrap.index_regex.match( key )
      if m:
        i = int( m.group(1) )
        if i < len(list(self.e)):
          e = list(self.e)[i]

    # if e is still None, we didn't find an element and
    # we need to return None
    if e is None:
      return None

    # we have the element now. we need
    # to determine if there is a value to return, or
    # if we should return another wrapped element

    # if the element has children,
    # wrap it and return it
    if len(list(e)) > 0:
      return ETWrap(e)
      
    # if the element has type information, use it
    # convert element text to the correct type
    eval_str = "%s(%s)" % (e.attrib.get('type','str'), e.text)
    try:
      val = eval(eval_str)
    except:
      val = e.text

    return val

  __getitem__ = __getattr__
  __call__    = __getattr__

def gettipkeys( data,separator='/' ):
  return DataTree._get_tippaths( data, separator )

