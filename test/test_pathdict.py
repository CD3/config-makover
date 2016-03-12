import math, os, sys
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.utils import *

def test_operations():

  data = { 'one' : 1
         , 'two' : 2
         , 'l1'  : { 'one' : 11
                   , 'two' : 12
                   , 'l2'  : { 'one' : 121 }
                   }
         }

  pdata = PathDict( data )

  assert pdata.get('one') == 1
  assert pdata.get('l1/one') == 11

  assert pdata.get_node('/l1').path == '/l1'
  assert pdata.get_node('l1').path == '/l1'
  assert pdata.get_node('/l1/l2').path == '/l1/l2'
  assert pdata.get_node('l1/l2').path == '/l1/l2'
  assert pdata.get_node('l1').get_node('./').path == '/l1'
  assert pdata.get_node('l1').get_node('l2').path == '/l1/l2'
  assert pdata.get_node('l1').get_node('l2').get_node('..').path == '/l1'

  pdata.set( '/l1/one', 'one' )
  pdata.set( '/l1/three', 3 )

  assert data['l1']['one'] == 'one'
  assert data['l1']['three'] == 3

  assert pdata['l1/l2/one'] == 121
  pdata['l1/l2/one'] += 1
  assert pdata['l1/l2/one'] == 122

  pdata = pdata.get_node('l1')

  assert pdata['one'] == 'one'
  assert pdata['/one'] == 1
  assert pdata['l2/one'] == 122
  assert pdata['/l1/l2/one'] == 122
            



