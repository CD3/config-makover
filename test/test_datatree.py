import math, os, sys
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.DataTree import *
import pytest
import utils


def test_operations():

  data = { 'one' : 1
         , 'two' : 2
         , 'l1'  : { 'one' : 11
                   , 'two' : 12
                   , 'l2'  : { 'one' : 121 }
                   }
         }
  pdata = DataTree( data )


  assert pdata.get('one') == 1
  assert pdata.get('l1/one') == 11

  assert pdata.get_node('/l1').root == '/l1/'
  assert pdata.get_node('l1').root == '/l1/'
  assert pdata.get_node('/l1/l2').root == '/l1/l2/'
  assert pdata.get_node('l1/l2').root == '/l1/l2/'
  assert pdata.get_node('l1').get_node('./').root == '/l1/'
  assert pdata.get_node('l1').get_node('l2').root == '/l1/l2/'
  assert pdata.get_node('l1').get_node('l2').get_node('..').root == '/l1/'

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
            

def test_spec():
  data = DataTree( { 'one' : '1'
                   , 'two' : '2'
                   , 'l1'  : { 'one' : '11.1'
                             , 'two' : '12.2'
                             , 'l2'  : { 'one' : '121' }
                             }
                   } )
  data.set_spec( '/one/type', 'int' )
  data.set_spec( '/two/type', 'int' )
  data.set_spec( '/l1/one/type', 'float|int' )
  data.set_spec( '/l1/two/type', 'float' )

  assert data['one'] == 1
  assert data['two'] == 2
  assert data['l1/one'] == 11
  assert data['l1/two'] == 12.2
  assert data.get('l1/two','float|int') == 12
  assert data['l1/two','float|int'] == 12


  data = DataTree( { 'one' : '1'
                   , 'two' : '2'
                   , 'l1'  : { 'one' : '11.1'
                             , 'two' : '12.2'
                             , 'l2'  : { 'one' : '121' }
                             }
                   } )
  data.add_spec( '/**', 'type', 'float|int' )

  assert data['one'] == 1
  assert data['two'] == 2
  assert data['l1/one'] == 11
  assert data['l1/two'] == 12

def test_type_casting():
  data = DataTree( { 'length' : '1 cm'
                   , 'width'  : '2 inch'
                   } )
  data.add_spec( '/**', 'type', 'Q|mag' )

  # print data['length']
  # print data['width']

def test_units():
  # TODO: need to test temperature conversions
  data = DataTree({ 'length' : '1 cm'
                   ,'width'  : '2 inch'
                  } )

  data.add_spec( '**', 'type', 'Q' )


  assert isinstance( data['length'], pint.quantity._Quantity )
  assert isinstance( data['width'], pint.quantity._Quantity )

  assert data['length'].magnitude == 1
  assert utils.Close(data.get('length',unit='inch').magnitude, 1/2.54, 1e-5)
  assert data['width'].magnitude == 2
  assert utils.Close(data.get('width',unit='cm').magnitude, 2*2.54, 1e-5)



  data = DataTree({ 'length' : '1 cm'
                   ,'width'  : '2 inch'
                  } )


  assert data.get('length',unit='cm'  ).magnitude == 1
  assert utils.Close( data.get('length',unit='inch').magnitude, 1/2.54, 1e-5)
  assert data.get('width', unit='inch').magnitude == 2
  assert utils.Close(data.get('width', unit='cm'  ).magnitude, 2*2.54, 1e-5)


def test_default():
  data = { 'one' : 1
         , 'two' : 2
         , 'l1'  : { 'one' : 11
                   , 'two' : 12
                   , 'l1'  : { 'one' : 111 }
                   }
         , 'l2'  : { 'one' : 21
                   , 'two' : 22
                   }
         }
  pdata = DataTree( data )
  pdata.set_spec( 'two/default', 200 )
  pdata.set_spec( 'three/default', 300 )
  pdata.set_spec( 'l1/two/default', 200 )
  pdata.set_spec( 'l1/three/default', 300 )
  pdata.set_spec( 'l1/l1/two/default', 200 )
  pdata.set_spec( 'l1/l1/three/default', 300 )


  assert pdata.get('one') == 1
  assert pdata.get('two') == 2
  assert pdata.get('three') == 300
  assert pdata.get('l1/one') == 11
  assert pdata.get('l1/two') == 12
  assert pdata.get('l1/three') == 300
  assert pdata.get('l1/l1/one') == 111
  assert pdata.get('l1/l1/two') == 200
  assert pdata.get('l1/l1/three') == 300

  with pytest.raises(KeyError):
    pdata.get('four')
  with pytest.raises(KeyError):
    pdata.get('l1/four')
  with pytest.raises(KeyError):
    pdata.get('l1/l1/four')
  with pytest.raises(KeyError):
    pdata.get('l1/l2/one')


  assert     pdata.has('one')
  assert     pdata.has('two')
  assert not pdata.has('three')
  assert     pdata.has('l1/one')
  assert     pdata.has('l1/two')
  assert not pdata.has('l1/three')
  assert     pdata.has('l1/l1/one')
  assert not pdata.has('l1/l1/two')
  assert not pdata.has('l1/l1/three')


  # insert defaults
  for k in pdata.get_spec_paths( '**/default' ):
    v = pdata.get_spec(k)
    k = re.sub( '/default$', '', k )
    if not pdata.has(k):
      pdata.set(k,v)

  assert pdata.get('one') == 1
  assert pdata.get('two') == 2
  assert pdata.get('three') == 300
  assert pdata.get('l1/one') == 11
  assert pdata.get('l1/two') == 12
  assert pdata.get('l1/three') == 300
  assert pdata.get('l1/l1/one') == 111
  assert pdata.get('l1/l1/two') == 200
  assert pdata.get('l1/l1/three') == 300

  with pytest.raises(KeyError):
    pdata.get('four')
  with pytest.raises(KeyError):
    pdata.get('l1/four')
  with pytest.raises(KeyError):
    pdata.get('l1/l1/four')
  with pytest.raises(KeyError):
    pdata.get('l1/l2/one')

  assert     pdata.has('one')
  assert     pdata.has('two')
  assert     pdata.has('three')
  assert     pdata.has('l1/one')
  assert     pdata.has('l1/two')
  assert     pdata.has('l1/three')
  assert     pdata.has('l1/l1/one')
  assert     pdata.has('l1/l1/two')
  assert     pdata.has('l1/l1/three')


def test_searching():
  data = { '1' : 1
         , '2' : 2
         , '3' : 3
         , 'l1' : { '1' : 11
                  , '2' : 12
                  , 'l1' : { '1' : 111 }
                  }
         }

def test_custom_types():
  class myType:
    def __init__(self):
      self.data = 12345
    def __str__(self):
      return str(self.data)

  data = { 'one' : 1
         , 'two_point_one' : 2.1
         , 'myType' : myType()
         }

  data = DataTree(data)

  assert isinstance(data['one'],int)
  assert isinstance(data['two_point_one'],float)
  assert isinstance(data['myType'],myType)

  assert str(data['one']) == '1'
  assert str(data['two_point_one']) == '2.1'
  assert str(data['myType'].data) == '12345'
  assert str(data['myType']) == '12345'

def test_misc():
  pass
