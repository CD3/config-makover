#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *

import utils
#logging.basicConfig( level=logging.DEBUG )

def test_level_filter():
  text = '''
  var : 1
  nest :
    var : 2
    nest :
      var : 3
      nest :
        var : 4
        nest :
          var : 5
          nest :
            var : 6
  '''

  def filter_on_layer( val, key ):
    if not isinstance(val, dict):
      if len( key.split('.') ) % 2 == 0:
        return str(val)
      else:
        return float(str(val))

    return val

  data = readConfig( text, filter=filter_on_layer )

  assert isinstance( data['var'], str)
  assert isinstance( data['nest']['var'], float)
  assert isinstance( data['nest']['nest']['var'], str)
  assert isinstance( data['nest']['nest']['nest']['var'], float)
  assert isinstance( data['nest']['nest']['nest']['nest']['var'], str)
  assert isinstance( data['nest']['nest']['nest']['nest']['nest']['var'], float)

  print data

