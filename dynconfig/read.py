from render import render as render_dict
from .parsers import *

import re


funcRegex = re.compile('^\s*([^\s\(]+)\(([^\)]*)\)\s*')

def include_func(fn, context):
  with open(fn) as f:
    text = f.read()
  return context['parser'](text)

def DataTable_func(fn, context):
  return DataTable(fn)
  
funcs = { 'include' : include_func
        , 'DataTable' : DataTable_func }

def get_func_and_args(v):
  if not isinstance(v,(str,unicode)):
    return None,None

  m = funcRegex.match(v)
  if m is None:
    return None,None
    
  f = m.groups()[0].strip(''' \t\n'"''')
  a = m.groups()[1].split(',')
  for i in range(len(a)):
    a[i] = eval(a[i].strip())

  return f,a


def readConfig( text = None, parser = yaml.load
                           , render = True
                           , ignore_unparsed_expressions = False
                           , return_pdict = False
                           , filename = None):
  '''
  Read string (or file) containing configuration data into a data tree.

  :param text: String containing configuration file text
  
  :param parser: A callable that can parse the configuration text into a configuration tree. For example,
  ``parser=yaml.load`` or ``parser=json.loads``.

  :param render: Attempt to render the configuration tree.

  :param filename: Configuration filename. If given, ``text`` parameter is ignored.

  '''
  # if a filename is given, read it into the text string
  if filename:
    with open(filename) as f:
      text = f.read()

  # read the data from the string into a tree
  data = pdict()
  data.update(parser(text))

  # for p in get_all_pdict_keys(data):
    # f,a = get_func_and_args( data[p] )
    # if not f is None and f in funcs:
      # data[p] = funcs[f]( *a, context = {'parser' : parser} )

  # if render is set, we want to render the data tree
  if render:
    data = render_dict( data, repeat=True, strict=not ignore_unparsed_expressions)

  if return_pdict:
    return data

  return data.dict()
