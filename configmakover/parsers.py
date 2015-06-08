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
