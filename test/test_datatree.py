import math, os, sys
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.DataTree import *


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
  data.new_spec( '/**', 'type', 'float|int' )

  assert data['one'] == 1
  assert data['two'] == 2
  assert data['l1/one'] == 11
  assert data['l1/two'] == 12

def test_type_casting():
  data = DataTree( { 'length' : '1 cm'
                   , 'width'  : '2 inch'
                   } )
  data.new_spec( '/**', 'type', 'Q|mag' )

  # print data['length']
  # print data['width']

def test_units():

  data = DataTree({ 'length' : '1 cm'
                   ,'width'  : '2 inch'
                  } )

  data.new_spec( '**', 'type', 'Q' )


  assert isinstance( data['length'], pint.quantity._Quantity )
  assert isinstance( data['width'], pint.quantity._Quantity )

  assert data['length'].magnitude == 1
  assert data.get('length',unit='inch').magnitude == 1/2.54
  assert data['width'].magnitude == 2
  assert data.get('width',unit='cm').magnitude == 2*2.54



  data = DataTree({ 'length' : '1 cm'
                   ,'width'  : '2 inch'
                  } )


  assert data.get('length',unit='cm'  ).magnitude == 1
  assert data.get('length',unit='inch').magnitude == 1/2.54
  assert data.get('width', unit='inch').magnitude == 2
  assert data.get('width', unit='cm'  ).magnitude == 2*2.54




def test_searching():
  data = { '1' : 1
         , '2' : 2
         , '3' : 3
         , 'l1' : { '1' : 11
                  , '2' : 12
                  , 'l1' : { '1' : 111 }
                  }
         }

def test_misc():
  pass
