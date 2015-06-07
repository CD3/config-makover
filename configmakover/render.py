
from mako.template import Template
import yaml
import dpath.util

def iterator( obj ):
  if isinstance( obj, dict ):
    return obj
  if isinstance( obj, list ):
    return xrange( len( obj ) )
  return None

class AttrDict(dict):
  '''A dict that allows attribute style access'''
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__

def toAttrDict( d ):
  it = iterator( d )
  if it:
    for i in it:
      d[i] = toAttrDict( d[i] )

  if isinstance( d, dict ):
    return AttrDict( d )
  else:
    return d

def renderTree( data, imports = None, strict_undefined = True ):
  '''Renders a nested data structure with itself. Redering is done recursivly
  and repeated until a render does not yeild a change.'''


  input_text = ''
  # dump the tree to a YAML string
  output_text = yaml.dump(data, default_flow_style=False)
  # keep rendering until the YAML string representation of the tree does not change
  while input_text != output_text:
    input_text = output_text
    # run the YAML string through a Mako template using the tree for context
    t = Template(input_text, imports=imports, ignore_expression_errors=True)
    output_text = t.render( **toAttrDict(data) )
    data = yaml.load( output_text )


  # run make one more time with strict errors so that we will get
  # an exception if there are still any expressions left
  if strict_undefined:
    t = Template(input_text, strict_undefined=True, ignore_expression_errors=False)
    output_text = t.render( )

  return data

def scopedRenderTree( data, imports = None, strict_undefined = True ):
  'a''Renders a nested data structure with itself. Redering is done recursivly and repeated until a render does not yeild a change.'''

  def singlePass( data ):
    it = iterator( data )
    if it:
      for i in it:
        data[i] = singlePass( data[i] )
    else:
      return data

    data = renderTree(data, imports=imports, strict_undefined=False)

    return data

  input_text = ''
  output_text = yaml.dump(data, default_flow_style=False)
  # run data through rendering until it doesn't change anymore
  while input_text != output_text:
    input_text = output_text
    data = singlePass(data)
    output_text = yaml.dump(data, default_flow_style=False)

  if strict_undefined:
    # run make one more time with strict errors so that we will get
    # an exception if there are still any expressions left
    t = Template(input_text, strict_undefined=True, ignore_expression_errors=False)
    output_text = t.render( )

  return data

