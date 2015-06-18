
import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.validate import *
from configmakover.read import *

def test_simple():

  data_text   = '''
  var1 : 1
  var2 : 2
  nest1 :
    var1 : "11"
    nest2 :
      var1 : 111
      var2 : 112
      nest3 :
        - 1111
        - 1112
        - 1113
  '''

  schema_text = '''
  var1 : { type : number }
  var2 :
    type : number
    #min : 1.5
  nest1 :
    type : dict
    schema :
      var1 : { type : string }
      var2 : { test : { one.two : 'what?'} }
      nest2 :
        type : dict
        schema :
          var1 : { type : number }
          var2 : { type : number }
          nest3 :
            type : list
            test : 'huh?'
  '''

  data   = readConfig(   data_text )
  schema = readSchema( schema_text )

  validate( data, schema )

