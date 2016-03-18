import inspect, re, os
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
