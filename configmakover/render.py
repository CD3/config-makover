from .utils import *
from .filters import *
from tempita import Template
import yaml

import dicttoxml, lxml.etree, xmldict

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

def renderDictTree( data, context = {}, imports = None, filters = toNum, strict = False ):
  '''Renders'''
  
  # get xml version of the data
  data_xml = dicttoxml.dicttoxml( data )

  data = renderXMLTree( data_xml, context, imports, filters, strict )

  return data

def renderXMLTree( data_xml , context = {}, imports = None, filters = toNum, strict = False ):

  # get an etree of the data
  data_tree = lxml.etree.fromstring( data_xml )
  # explicitly set the type data for any elements
  # that have a @*_type data specified.
  for e in data_tree.iter():
    tmp = "@%s_type" % e.tag
    # check for a type entry
    ee = e.find("../key[@name='%s']" % tmp)
    if not ee is None:
      e.attrib['type'] = ee.text

  # remove metadata entries
  rem = []
  for e in data_tree.iter():
    if e.tag == 'key' and 'name' in e.attrib:
      if re.match( "@.*_type", e.attrib['name'] ):
        rem.append(e)
  for e in rem:
    e.getparent().remove(e)


  def local_lookup(element, path):
    # tag names are relative to element, so we need
    # to look for them in element's parent
    parent = element.getparent()
    if parent is None:
      return None

    # look for an element with the tag
    e = parent.find(path)
    if e is None:
      return None

    # get the data type, if available
    vtype = e.attrib.get('type','str')
    vval  = e.text

    # convert element text to the correct type
    # we need to do this, even though it is just going to get turned back into text in the XML
    # because it the expression might be trying to use it in a calculation.
    eval_str = "%s(%s)" % (vtype,vval)
    try:
      val = eval(eval_str)
    except:
      val = vval

    return val

  def global_lookup(element, path):
    e = element
    while element.getparent():
      e = element.getparent()

    vtype = e.attrib.get('type','str')
    vval  = e.text

    eval_str = "%s(%s)" % (vtype,vval)
    try:
      val = eval(eval_str)
    except:
      val = vval

    return val

  # build the python block for importing the modules listed
  if isinstance( imports, str ):
    imports = [imports]
  imports_text = ""
  if imports:
    imports_text += "{{py:\n"
    imports_text += "import "
    imports_text += ", ".join( imports )
    imports_text += "\n}}"


  # now render the tree
  # keep rendering until the xml string repeats itself.
  hashes = dict()
  hasher = hashlib.sha1
  hash = hasher(  lxml.etree.tostring(data_tree) ).hexdigest()
  # apply the filters
  while hashes.get( hash, 0 ) < 2:
    # run every elment text through tempita
    for e in data_tree.iter():
      if not e.text is None:
        e.text = tempita.sub( imports_text+e.text, l=lambda x : local_lookup(e,x) , g=lambda x : global_lookup(data_tree,x) )

    # apply filters
    applyFiltersETree( data_tree, filters )
    hash = hasher(  lxml.etree.tostring(data_tree) ).hexdigest()
    hashes[hash] = hashes.get(hash,0) + 1

    
  # get xml of new tree
  data_text = lxml.etree.tostring( data_tree )

  # de-serialize data to nested dict
  data = xmldict.xml_to_dict( data_text )

  # cast all text items to data
  def cast( d ):
    # if the dict has a #text element, we want cast the text to a type
    # and return it
    if isinstance( d, dict ) and '#text' in d:
      try:
        eval_str = "{@type}({#text})".format(**d)
        v = eval(eval_str)
      except:
        v = d['#text']

      d = v

    # if d is iterable, then we need to loop through all items
    # and cast each one
    it = iterator( d )
    if it:
      for i in it:
        d[i] =  cast( d[i] )

    return d

  data = cast( data )['root']

  if strict:
    s = CheckForExpressions(data)
    if s:
      raise RuntimeError(ExpressionErrorMsg % s )

  return data




