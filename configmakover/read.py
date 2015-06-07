

from .render import *
import mako.template
import re

def readConfig( text = None, parser = yaml.load
                           , render = True
                           , preprocess = True
                           , filename = None):
  '''Read string (or file) containing configuration data into a data tree.'''

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

  # if render is set, we want to render the data tree
  if render:
    data = scopedRenderTree(data, imports=imports)
  
  return data
