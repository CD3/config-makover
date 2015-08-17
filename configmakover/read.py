from .render import *
from .filters import toNum
from tempita import Template
import re

def readConfig( text = None, parser = yaml.load
                           , preprocess = True
                           , render = True
                           , pre_filters = None
                           , render_filters = None
                           , post_filters = None
                           , ignore_expression_errors = False
                           , filename = None):
  '''
  Read string (or file) containing configuration data into a data tree.

  :param text: String containing configuration file text
  
  :param parser: A callable that can parse the configuration text into a configuration tree. For example,
  ``parser=yaml.load`` or ``parser=json.loads``.

  :param preprocess: Preprocess the configuration text as a template before loading.

  :param render: Attempt to render the configuration tree.

  :param pre_filters: A set of functions to call on each entry of the data tree before rendering begins.

  :param render_filters: A set of functions to call on each entry of the data
    tree as it is being renderd. These functions will be applied after each call to Template.render().

  :param post_filters: A set of functions to call on each entry of the data tree after rendering is complete.

  :param filename: Configuration filename. If given, ``text`` parameter is ignored

  '''

  # if a filename is given, read it into the text string
  if filename:
    with open(filename) as f:
      text = f.read()

  # if preprocess is set, we want to run the text through the template engine
  imports = []
  if preprocess:
    # we need to extract imported modules so we can import them
    # during the render process
    r1 = re.compile("{{\s*py:\s*[^}]*}}", re.MULTILINE) # to extract the python blocks
    r2 = re.compile("^\s*import\s*(.*)\s*$")     # to extract modules from import statements
    for m1 in r1.finditer( text ):
      for l in m1.group().splitlines():
        for m2 in r2.finditer( l ):
          imports.append( m2.group(1) )

    t = Template( text )
    text = t.substitute()

  # read the data from the string into a tree
  data = parser( text )

  # if pre filters where given, apply them
  if not pre_filters is None:
    data = applyFiltersToDict(data, pre_filters)

  # if render is set, we want to render the data tree
  if render:
    data = renderDictTree( data, imports=imports, filters=render_filters, strict=not ignore_expression_errors )

  # if post filters where given, apply them
  if not post_filters is None:
    data = applyFiltersToDict(data, post_filters)
  
  return data


readSchema = readConfig
