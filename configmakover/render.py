from .utils import *
from .filters import *
from tempita import Template
import yaml
import dpath

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

def renderDictTree( data, context = {}, imports = None, filters = toNum, strict = False ):
  '''Renders a dictionary'''
  
  print [ x[0] for x in dpath.util.search( data, '**', yielded=True ) ]
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

    e = e.find( path )
    if e is None:
      return None

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
        e.text = tempita.sub( imports_text+e.text, l=ETWrap(e.getparent()) , g=ETWrap(data_tree) )

    # apply filters
    applyFiltersToETree( data_tree, filters )
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




