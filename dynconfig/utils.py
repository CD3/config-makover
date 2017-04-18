from collections import Mapping, Sequence, Container
from pdict import pdict

STR_TYPES = (str,unicode)
def iterator( obj ):
  if isinstance( obj, Mapping ):
    return obj
  if isinstance( obj, Sequence) and not isinstance( obj, STR_TYPES ):
    return xrange( len( obj ) )
  return None

def get_all_pdict_keys(d):
  '''Get all keys for all (terminal) elements in a pdict.'''
  keys = []
  for k in d.keys():
    if isinstance(d[k],pdict):
      keys += [ d.delimiter + str(k) + p for p in get_all_pdict_keys(d[k]) ]
    else:
      keys.append(d.delimiter+str(k))
  return keys

def transform(d,f):
  for k in get_all_pdict_keys(d):
    try:
      d[k] = f(d[k])
    except:
      pass
