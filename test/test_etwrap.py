import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.utils import *
import dicttoxml

def test_etwrap():
  
  data = { 'var1' : 1
         , 'list1' : [ 2, 3, 4 ]
         , 'nest1' : { 'var1' : 11 }
         }

  tree = lxml.etree.fromstring( dicttoxml.dicttoxml( data ) )
  wrap = ETWrap( tree )

  assert wrap.var1 == 1
  assert wrap['var1'] == 1
  assert wrap('var1') == 1
  assert wrap.nest1.var1 == 11
  assert wrap['nest1']['var1'] == 11
  assert wrap('nest1')('var1') == 11
  assert wrap['nest1'].var1 == 11
  assert wrap('nest1').var1 == 11
  assert wrap('nest1/var1') == 11
  assert wrap('nest1/var1') == 11
  assert wrap.list1._0 == 2
  assert wrap.list1._1 == 3
  assert wrap.list1._2 == 4
