from .utils import *
from .filters import *
from tempita import Template
import yaml
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



loader = pickle.loads
dumper = pickle.dumps
#loader = yaml.load
#dumper = yaml.dump

def CheckForExpressions(data):
    serialized_data = dumper(data)
    m = re.search("{{[^}]+}}", serialized_data)
    if m:
      s = serialized_data[m.start():m.end()]
      return s
    else:
      return None

ExpressionErrorMsg = "One or more expressions where not replaced. The first one was '%s', but there may be others."

def renderTree( data, context = {}, imports = None, filters = toNum, strict = False ):
  '''Renders a nested data structure with itself.

     Given a data tree that contains some parameters containing references to
     other parmaeters,

     param2 : {{param1}}

     this function will replace parameter references with thier values.
     Tempita is used for the rendering with the following steps
     
      - the data tree is written to a data string
      - the data string loaded as a Tempita template
      - the data string s rendered using the data tree as the context
      - the data string is decoded back to a data tree, replacing the original

     These steps repeated until a the data string is unchanged by a render.
     '''

  # build the python block for importing the modules listed
  if isinstance( imports, str ):
    imports = [imports]
  imports_text = ""
  if imports:
    imports_text += "{{py:\n"
    imports_text += "import "
    imports_text += ", ".join( imports )
    imports_text += "\n}}"

  # dump the tree to a string
  serialized_data = dumper(data)
  # keep rendering until the data string repeats itself.
  hashes = dict()
  hasher = hashlib.sha1
  hash = hasher(serialized_data).hexdigest()
  # apply the filters
  data = applyFilters(data, filters)
  while hashes.get( hash, 0 ) < 2:
    # run the string through a Tempita template using the tree for context
    logging.debug("RENDERING (%s)" % hash)
    logging.debug( serialized_data )
    logging.debug( data )
    t = Template(imports_text+serialized_data)
    if isinstance(data,Mapping):
      data = dict2bunch(data)
    else:
      data = {'this' : data }
    serialized_data = t.substitute( dict2bunch( dict(context,**data) ) )
    data = loader( serialized_data )
    # apply filters and update data string
    data = applyFilters(data, filters)
    serialized_data = dumper(data)
    hash = hasher(serialized_data).hexdigest()
    hashes[hash] = hashes.get(hash,0) + 1
    logging.debug("RENDERED (%s)" % hash)
    logging.debug( serialized_data )

  if strict:
    s = CheckForExpressions(data)
    if s:
      raise RuntimeError(ExpressionErrorMsg % s )

  return data

def scopedRenderTree( data, imports = None, filters = toNum, strict = True ):
  '''Render a data tree by applying the renderTree function to each branch, starting from the bottom.

     This function also acts recursivly. It 'walks' down the data tree until
     it reaches the end of a branch. The renderTree function is applied to each branch
     on the way back up. This allows support for 'local' and 'global' scopes. All parameter
     references will be replaced by values from parameters in the same branch as the reference
     if possible. If no such parameter exists, then the first branch containg the parmeter name
     will be used.
  '''
  def singlePass( d ):
    '''A single pass through the entire tree'''
    # walk down tree first
    # first, check if data is iterable.
    it = iterator( d )
    if it:
      # if so, loop through all items
      for i in it:
        # an item is iterable, call ourself...
        if iterator( d[i] ):
          d[i] = singlePass( d[i] )
    else:
      # if not, return immediatly
      return d

    # now re can render the data. by calling this after the loop
    # above, we will render the bottom branches first
    d = renderTree(d, context=dict2bunch({'top':data}), imports=imports, strict=False, filters=filters)

    # return the rendered data.
    return d

  # render the data until it does not change anymore.
  # we want to catch circular dependencies, so we'll keep a record of all
  # string representations of the data.

  # dump the tree to a string
  serialized_data = dumper(data)
  # setup data string record. we will just store the hashes.
  hashes = dict()
  hasher = hashlib.sha1
  hash = hasher(serialized_data).hexdigest()
  # keep rendering until the data string repeats itself.
  while hashes.get( hash, 0 ) < 2:
    data = singlePass(data)
    serialized_data = dumper(data)
    hash = hasher(serialized_data).hexdigest()
    hashes[hash] = hashes.get(hash,0) + 1

  if strict:
    s = CheckForExpressions(data)
    if s:
      raise RuntimeError(ExpressionErrorMsg % s )

  return data

