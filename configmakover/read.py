from .render import *
from .filters import toNum
import mako.template
import re

def readConfig( text = None, parser = yaml.load
                           , preprocess = True
                           , render = True
                           , pre_filters = None
                           , render_filters = None
                           , post_filters = None
                           , filename = None):
  '''
  Read string (or file) containing configuration data into a data tree.

  :param text: String containing configuration file text
  
  :param parser: A callable that can parse the configuration text into a configuration tree. For example,
  ``parser=yaml.load`` or ``parser=json.loads``.

  :param preprocess: Preprocess the configuration text as a Mako template before loading.

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

  # if preprocess is set, we want to run the text through Mako
  imports = None
  if preprocess:
    t = Template(text, ignore_expression_errors=True)
    # Mako blocks will be stripped out of the steam during this pass,
    # so we need to get module imports and variable settings so we can pass them
    # to the next calls
    regex = re.compile("(import )|(^[a-zA-Z].*=)")
    imports = [ line for line in t.code.split('\n') if not regex.search( line ) is None ][3:]
    text = t.render()

  # read the data from the string into a tree
  data = parser( text )

  # if pre filters where given, apply them
  if not pre_filters is None:
    data = applyFilters(data, pre_filters)

  # if render is set, we want to render the data tree
  if render:
    data = scopedRenderTree( {'top' : data}, imports=imports, filters=render_filters )
    data  = data['top']

  # if post filters where given, apply them
  if not post_filters is None:
    data = applyFilters(data, post_filters)
  
  return data


readSchema = readConfig
