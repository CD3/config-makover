
from mako.template import Template
import pickle, yaml, json
import hashlib
import dpath.util
import logging

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

def toNums( data ):
  '''Casts all data in a tree to numbers if possible'''
  for item in dpath.util.search( data, "**", yielded=True ):
    try:
      t = int
      if str(item[1]).find('.') > -1:
        t = float

      # TODO: add complex support
        
      dpath.util.set( data, item[0], t(str(item[1])) )
    except ValueError:
      pass

  return data

def toAttrDict( d ):
  '''Replaces all intances of dict() with AttrDict() in a data tree.'''
  it = iterator( d )
  if it:
    for i in it:
      d[i] = toAttrDict( d[i] )

  if isinstance( d, dict ):
    return AttrDict( d )
  else:
    return d




loader = pickle.loads
dumper = pickle.dumps
#loader = yaml.load
#dumper = yaml.dump
#loader = json.loads
#dumper = json.dumps


def renderTree( data, imports = None, strict_undefined = True ):
  '''Renders a nested data structure with itself.

     Given a data tree that contains some parameters containing references to
     other parmaeters,

     param2 : ${param1}

     this function will replace parameter references with thier values.
     Mako Templates are used for the rendering with the following steps
     
      - the data tree is written to a data string
      - the data string loaded as a Mako template
      - the data string s rendered using the data tree as the context
      - the data string is decoded back to a data tree, replacing the original

     These steps repeated until a the data string is unchanged by a render.
     '''

  # dump the tree to a string
  serialized_data = dumper(data)
  # keep rendering until the data string repeats itself.
  hashes = dict()
  hasher = hashlib.sha1
  hash = hasher(serialized_data).hexdigest()
  while hashes.get( hash, 0 ) < 2:
    # run the string through a Mako template using the tree for context
    logging.debug("RENDERING (%s)" % hash)
    logging.debug( serialized_data )
    t = Template(serialized_data, imports=imports, ignore_expression_errors=True)
    serialized_data = t.render( **toAttrDict(data) )
    data = loader( serialized_data )
    # turn everything we can into a number and update output_text
    data = toNums(data)
    serialized_data = dumper(data)
    hash = hasher(serialized_data).hexdigest()
    hashes[hash] = hashes.get(hash,0) + 1
    logging.debug("RENDERED (%s)" % hash)
    logging.debug( serialized_data )


  # run make one more time with strict errors so that we will get
  # an exception if there are still any expressions left
  if strict_undefined:
    t = Template(input_text, strict_undefined=True, ignore_expression_errors=False)
    output_text = t.render( )

  return data

def scopedRenderTree( data, imports = None, strict_undefined = True ):
  '''Render a data tree by applying the renderTree function to each branch, starting from the bottom.

     This function also acts recursivly. It 'walks' down the data tree until
     it reaches the end of a branch. The renderTree function is applied to each branch
     on the way back up. This allows support for 'local' and 'global' scopes. All parameter
     references will be replaced by values from parameters in the same branch as the reference
     if possible. If no such parameter exists, then the first branch containg the parmeter name
     will be used.
  '''




  def singlePass( data ):
    '''A single pass through the entire tree'''

    # walk down tree first
    # first, check if data is iterable.
    it = iterator( data )
    if it:
      # if so, loop through all items
      for i in it:
        # an item is iterable, call ourself...
        if iterator( data[i] ):
          data[i] = singlePass( data[i] )
    else:
      # if not, return immediatly
      return data

    # now re can render the data. by calling this after the loop
    # above, we will render the bottom branches first
    data = renderTree(data, imports=imports, strict_undefined=False)

    # return the rendered data.
    return data

  input_text = ''
  output_text = dumper(data)
  # run data through rendering until it doesn't change anymore
  while input_text != output_text:
    input_text = output_text
    data = singlePass(data)
    output_text = dumper(data)

  if strict_undefined:
    # run make one more time with strict errors so that we will get
    # an exception if there are still any expressions left
    t = Template(input_text, strict_undefined=True, ignore_expression_errors=False)
    output_text = t.render( )

  return data

