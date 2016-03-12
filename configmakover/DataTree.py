import os
import dpath
class DataTree(object):
  '''Simple wrapper for nested dicts that allows accessing dict elements with paths like a filesystem.'''
  def __init__(self, d = dict(), p = '/', s = dict()):
    self.root = p
    self.data = d
    self.spec = s

  def _join(self,*args):
    return os.path.normpath( os.path.join( *args ) )

  def _abspath(self,p):
    if p[0] == '/':
      path = p
    else:
      path = self._join( self.root, p )

    return os.path.normpath( path )

  def __getitem__(self,k):
    return self.get(k)

  def __setitem__(self,k,v):
    return self.set(k,v)

  def get(self,p):
    path = self._abspath(p)
    val = dpath.util.get( self.data, path )
    try:
      # get the data type for this element
      # multiple types can be given
      v = val
      types = dpath.util.get( self.spec, self._join( path, 'type' ) )
      types = types.split('|')
      for t in types:
        t = eval(t)
        v = t(v)
      val = v
    except Exception as e:
      print e
      pass

    return val

  def set(self,p,v):
    return dpath.util.new( self.data, self._abspath(p), v )

  def get_node(self,p):
    '''Return a DataTree rooted at the path p.'''
    return DataTree( self.data, self._abspath( p )+'/' )

  def set_spec(self,p,v):
    return dpath.util.new( self.spec, self._abspath(p), v )

  def get_tippaths(self):
    keys = DataTree._gettipkeys( self.data, '/' )

    return keys


  @staticmethod
  def _get_tippaths( data,separator='/' ):
    '''Return a list of paths to the tips of a nested dict.'''
    keys = [ x[0] for x in dpath.util.search( data, '**', separator=separator, yielded=True ) ]

    # keys is a list of all keys in the data tree. we want to get a list of just the tips
    tipkeys = []
    for i in range(len(keys)):
      found = False
      for j in range(len(keys)):
        if i == j:
          continue
        if keys[j].startswith(keys[i]):
          found = True

      if not found:
        tipkeys.append( keys[i] )

    return tipkeys



