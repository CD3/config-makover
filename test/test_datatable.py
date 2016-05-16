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

  assert 'units' in data.spec

  assert data(0,0) == 0
  assert data(0,1) == 1
  assert data(1,0) == 1
  assert data(1,1) == 2

  assert data.get(0,0,'m').magnitude == 0
  assert utils.close( data.get(0,1,'1/m').magnitude, 1.e9 )
  assert utils.close( data.get(1,0,'m').magnitude, 1e-9 )
  assert utils.close( data.get(1,1,'1/m').magnitude, 2e9 )

