from .utils import *
from .filters import *
from .DataTree import *
from tempita import Template
import yaml
import dpath

import pickle
import hashlib
import logging
import re

# Replace the _eval function in the tempita.Template class
# so that we can ignore expression errors
_orig_eval = Template._eval
def _eval(self, code, ns, pos):
  __traceback_hide__ = True
  try:
    value = eval(code, self.default_namespace, ns)
  except:
    value = '{{'+code+'}}'

  return value
Template._eval = _eval

def CheckForExpressions(data):
    serialized_data = pickle.dumps(data)
    m = re.search("{{[^}]+}}", serialized_data)
    if m:
      s = serialized_data[m.start():m.end()]
      return s
    else:
      return None
ExpressionErrorMsg = "One or more expressions where not replaced. The first one was '%s', but there may be others."

# helper functions
def tableRow( table, x, cols, (units) ):
  pass


def renderDataTree( data, imports = [], setup = "", pre_filters = [], post_filters = [], filters = [], strict = False ):
  '''Renders a DataTree.'''
  # build the python block for importing the modules listed
  setup_text = ""
  if isinstance( imports, str ):
    imports = [imports]
  if not imports is None and len(imports) > 0:
    setup_text = ""
    setup_text += "{{py:\n"
    setup_text += "import "
    setup_text += ", ".join( imports )
    setup_text += "\n}}\n"

  # setup filters
  for f in filters:
    pre_filters.append( f )
    post_filters.append( f )

  # now render the tree
  # keep rendering until the tree repeats itself
  hashes = dict()
  hash =  hashlib.sha1( pickle.dumps(data) ).hexdigest()
  hashes[hash] = hashes.get(hash,0) + 1
  while hashes.get( hash, 0 ) < 2:
    keys = data.get_paths()
    for key in keys:
      for f in pre_filters:
        nargs = len(inspect.getargspec( f ).args)
        if nargs == 1:
          data[key] = f(data[key,'raw'])
        if nargs == 2:
          data[key] = f(data[key,'raw'], key)

      if isinstance( data[key,'raw'], (str,unicode) ):
        data[key] = tempita.sub( setup_text+data[key,'raw'], c=data.get_node( data._join( key,'..' )), Q_=DataTree.ureg.Quantity )

      for f in post_filters:
        nargs = len(inspect.getargspec( f ).args)
        if nargs == 1:
          data[key] = f(data[key,'raw'])
        if nargs == 2:
          data[key] = f(data[key,'raw'], key)

    hash =  hashlib.sha1( pickle.dumps(data) ).hexdigest()
    hashes[hash] = hashes.get(hash,0) + 1

  if strict:
    s = CheckForExpressions(data)
    if s:
      raise RuntimeError(ExpressionErrorMsg % s )

  return data

def renderDictTree( data, *args, **kwargs ):
  '''Renders a dictionary.'''
  return renderDataTree( DataTree(data), *args, **kwargs ).data




