import StringIO
import math, os, sys
import numpy
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path
from configmakover.DataTable import *
import utils

def test_simple():
  text = r'''
  # desc: sample data file
  # names: x y
  # units: nm dimensionless
  0 1
  1 2
  2 3
  3 4
  4 3
  5 2
  6 1
  '''

  data = DataTable()
  data.loads(text)

  for i in range(6):
    assert data(i,0) == i

  data(0,1) == 1
  data(1,1) == 2
  data(2,1) == 3
  data(3,1) == 4
  data(4,1) == 3
  data(5,1) == 2
  data(6,1) == 1

def test_units():
  text = r'''
  # names: wavelength probability
  # units: nm 1/nm
  0 1
  1 2
  2 3
  3 4
  4 3
  5 2
  6 1
  '''

  data = DataTable()
  data.loads(text)

  assert 'units' in data._spec

  assert data(0,0) == 0
  assert data(0,1) == 1
  assert data(1,0) == 1
  assert data(1,1) == 2

  assert data.get(0,0,'m').magnitude == 0
  assert utils.close( data.get(0,1,'1/m').magnitude, 1.e9 )
  assert utils.close( data.get(1,0,'m').magnitude, 1e-9 )
  assert utils.close( data.get(1,1,'1/m').magnitude, 2e9 )


def test_interpolation():
  text = r'''
  # names: wavelength probability
  # units: m 1/nm
  '''

  x = [ 0.1*i for i in range(0,100) ]
  for i in range(len(x)):
    text += str(x[i])
    text += " "
    text += str(math.sin(x[i]))
    text += "\n"
  
  data = DataTable()
  data.loads(text)
  Q_ = DataTable.ureg.Quantity

  assert utils.close( data.interp( 0.45,1 ), math.sin( 0.45 ) )
  assert utils.close( data.interp( 5.45,1 ), math.sin( 5.45 ) )

  assert utils.close( data.iget( 0.45,1 ).magnitude, math.sin( 0.45 ) )
  assert utils.close( data.iget( 5.45,1 ).magnitude, math.sin( 5.45 ) )

  assert utils.close( data.iget( 0.45,1,'1/m' ).magnitude, 1e9*math.sin( 0.45 ) )
  assert utils.close( data.iget( 5.45,1,'1/m' ).magnitude, 1e9*math.sin( 5.45 ) )

  assert utils.close( data.iget( Q_(0.45,'m'),1,'1/m' ).magnitude, 1e9*math.sin( 0.45 ) )
  assert utils.close( data.iget( Q_(5.45,'m'),1,'1/m' ).magnitude, 1e9*math.sin( 5.45 ) )

  assert utils.close( data.iget( Q_(0.45,'cm'),1,'1/m' ).magnitude, 1e9*math.sin( 0.0045 ) )
  assert utils.close( data.iget( Q_(5.45,'cm'),1,'1/m' ).magnitude, 1e9*math.sin( 0.0545 ) )

  assert utils.close( data.iget( Q_(45,'cm'),1,'1/m' ).magnitude,  1e9*math.sin( 0.45 ) )
  assert utils.close( data.iget( Q_(545,'cm'),1,'1/m' ).magnitude, 1e9*math.sin( 5.45 ) )

  assert utils.close( data.iget( '0.45 m' ).magnitude, math.sin( 0.45 ) )
  assert utils.close( data.iget( '5.45 m' ).magnitude, math.sin( 5.45 ) )

  assert utils.close( data.iget( '0.45 cm' ).magnitude, math.sin( 0.0045 ) )
  assert utils.close( data.iget( '5.45 cm' ).magnitude, math.sin( 0.0545 ) )

  assert utils.close( data.iget( '0.45' ).magnitude, math.sin( 0.45 ) )
  assert utils.close( data.iget( '5.45' ).magnitude, math.sin( 5.45 ) )



