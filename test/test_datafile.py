import StringIO
import math, os, sys
import numpy
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path
from configmakover.DataFile import *

def test_simple():
  text = r'''
  # desc: sample data file
  # name: x y
  # unit: nm dimensionless
  0 1
  1 2
  2 3
  3 4
  4 3
  5 2
  6 1
  '''

  data = DataFile()
  data.loads(text)

  for i in range(6):
    assert data[i,0] == i

  data[0,1] == 1
  data[1,1] == 2
  data[2,1] == 3
  data[3,1] == 4
  data[4,1] == 3
  data[5,1] == 2
  data[6,1] == 1

def test_units():
  text = r'''
  # name: wavelength probability
  # unit: nm dimensionless
  0 1
  1 2
  2 3
  3 4
  4 3
  5 2
  6 1
  '''

  data = DataFile()
  data.loads(text)
  print data.data
  print data.spec

  assert 'unit' in data.spec
  assert len(data.data) == 7
  assert data[0][0] == 0
  assert data[0][1] == 1
  assert data[1][0] == 1
  assert data[1][1] == 2

  assert data(0,0) == Quan0
  assert data(0,1) == 1
  assert data(1,0) == 1
  assert data(1,1) == 2

