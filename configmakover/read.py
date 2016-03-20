from .render import *
from .filters import toNum
from tempita import Template
import re

def readConfig( text = None, parser = yaml.load
                           , preprocess = True
                           , render = True
                           , pre_filters = []
                           , render_filters = []
                           , post_filters = []
                           , ignore_expression_errors = False
                           , spec = None
                           , pre_treeFilter = None
                           , post_treeFilter = None
                           , return_DataTree = False
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

  :param spec: A dict containing spec information for the data. Each entry in the dict will be added to the data tree using its add_spec function.

  :param pre_treeFilter: A function that will be passed the data tree after it has been de-serialized, but before it is rendered.

  :param post_treeFilter: A function that will be passed the data tree after it has been rendered.

  :param return_DataTree: If True, function will return a DataTree instance instead of a dict.

  :param filename: Configuration filename. If given, ``text`` parameter is ignored.

  '''

  if pre_filters is None:
    pre_filters = []
  if render_filters is None:
    render_filters = []
  if post_filters is None:
    post_filters = []

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
  data = DataTree(parser( text ))

  if spec:
    for k in spec:
      for kk in spec[k]:
        data.add_spec( k, kk, spec[k][kk] )

  if pre_treeFilter:
    data = pre_treeFilter(data)

  # if pre filters were given, apply them
  data = applyFiltersToDataTree(data, pre_filters)

  # if render is set, we want to render the data tree
  if render:
    data = renderDataTree( data, imports=imports, filters=render_filters, strict=not ignore_expression_errors )

  # if post filters were given, apply them
  data = applyFiltersToDataTree(data, post_filters)

  if post_treeFilter:
    data = post_treeFilter(data)
  
  if return_DataTree:
    return data
  else:
    return data.data


readSchema = readConfig
