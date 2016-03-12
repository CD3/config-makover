from .utils import *

import StringIO
import ConfigParser

class ini:

  @staticmethod
  def load( text ):
    parser = ConfigParser.ConfigParser()
    f = StringIO.StringIO(text)
    parser.readfp( f )
    f.close()

    data = dict()
    for sec in parser.sections():
      data[sec] = dict()
      for opt in parser.options(sec):
        data[sec][opt] = parser.get( sec, opt )

      
    return data


  @staticmethod
  def dump( data ):
    print "ini dump not implemented yet"

class keyval:
  '''A simple key=val style parser.'''

  @staticmethod
  def load( text, separator=None ):
    data = dict()
    for line in text.split('\n'):
      line = line.strip()
      if len(line) < 1 or line[0] == '#':
        continue

      tokens = line.split('=')
      if len(tokens) < 2:
        raise RuntimeError("Syntax Error: key (%s) found with no value. Expect 'key=val' format" % tokens[0])

      key = tokens[0]
      val = '='.join( tokens[1:] )
      val = val.split('#')[0] # throw away comments

      key = key.strip()
      val = val.strip()

      dpath.util.new(data,key,val,separator=separator)



    return data

  @staticmethod
  def dump( data ):
    keys = sorted( gettipkeys(data) )

    text = ""
    for i in range(len(keys)):
      k = keys[i]
      text += k
      text += " = "
      text += str( dpath.util.get( data, k ) )
      text += "\n"

    return text
