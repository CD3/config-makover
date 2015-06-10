
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
    var1 : "1"
  '''

  schema_text = '''
  var1 : { type : number }
  var2 :
    type : number
    min : 1.5
  nest1 :
    type : dict
    schema :
      var1 : { type : string }
  '''

  data = readConfig( data_text, render_filters = None )
  schema = readSchema( schema_text )

  validate( data, schema )


  pass
