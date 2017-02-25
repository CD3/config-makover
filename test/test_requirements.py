#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest
from utils import *

from dynconfig.render import *

def test_simple():
  logging.info("multi-pass")
  data = { 'size' : 100
          ,'x':
          { 'min' : -1.
          , 'max' : 2.
          , 'dx'  : '$( ({max} - {min}) / {/size} )'
          }
          ,'y':
          { 'min' : 1.
          , 'max' : 5.
          , 'dy'  : '$( ({max} - {min}) / {../size} )'
          }
          , 'layers' : [
                        {'thickness' : 0.1}
                       ,{'thickness' : 0.2}
                       ]
          , 'depth' : '$({layers/0/thickness} + {layers/1/thickness})'
         }

  rendered_data = render( data )

  assert rendered_data['x']['dx'] ==  (2.-(-1.))/100
  assert rendered_data['y']['dy'] ==  (5.-1.)/100

  assert type(rendered_data['x']['dx']) ==  float
  assert type(rendered_data['y']['dy']) ==  float

def test_misdirection():
  logging.info("multi-pass")
  data = { 'x' : 5
          ,'y' : '$(2*{x})'
          ,'z' : '$(2*{y})'
          , 'nested' : { 'x' : '$(2*{y})'
                        ,'y' : '$(2*{z})'
                        ,'z' : 15
                       }
         }

  rendered_data = render( data )

  assert rendered_data['x'] ==  5
  assert rendered_data['y'] ==  10
  assert rendered_data['z'] ==  20

  assert type(rendered_data['x']) ==  int
  assert type(rendered_data['y']) ==  int
  assert type(rendered_data['z']) ==  int

  assert rendered_data['nested']['x'] ==  60
  assert rendered_data['nested']['y'] ==  30
  assert rendered_data['nested']['z'] ==  15


def test_circular_dependency_detection():
  logging.info("circular dependency")
  data = { 'x' : 5
          ,'y' : '$(2*{z})'
          ,'z' : '$(2*{y})'
         }

  rendered_data = render( data )

  assert rendered_data['x'] ==  5

def test_replacement_types():
  '''Test that the type of expression replacements are as expected.'''
  logging.info("types")

  data = { 'x' : 5
          ,'y' : '$(2*{x})'
          ,'z' : '$(2.*{x})'
          ,'w' : ' $(2*{x})'
          ,'v' : '$(2*{x}) & $(3*{x})'
          ,'u' : '2x = $(2*{x}) and 3x = $(3*{x}).'
         }

  rendered_data = render( data, repeat=True )
  print rendered_data

  assert type(rendered_data['x']) ==  int
  assert type(rendered_data['y']) ==  int
  assert type(rendered_data['z']) ==  float
  assert type(rendered_data['w']) ==  str
  assert type(rendered_data['v']) ==  str
  assert type(rendered_data['u']) ==  str

  assert rendered_data['x'] ==  5
  assert rendered_data['y'] ==  10
  assert rendered_data['z'] ==  10.
  assert rendered_data['w'] ==  ' 10'
  assert rendered_data['v'] ==  '10 & 15'
  assert rendered_data['u'] ==  '2x = 10 and 3x = 15.'

def test_math():
  '''Test math module functions.'''
  logging.info("math")

  data = { 'x' : 5
          ,'y' : '$(m.sin({x}))'
          ,'z' : '$(m.pi)'
          ,'w' : -2
          ,'v' : '$(abs({w}))'
         }

  rendered_data = render( data )

  assert rendered_data['x'] ==  5
  assert rendered_data['y'] ==  Approx(math.sin(5))
  assert rendered_data['z'] ==  Approx(3.1415)
  assert rendered_data['w'] ==  -2
  assert rendered_data['v'] ==  2


def test_expression_filters():
  '''Test expression filters.'''
  logging.info("filters")

  data = { 'x' : 1.2345
          ,'y' : '$({x} | int )'
          ,'z' : '$({x} | ceil | int )'
          ,'w' : '$(25 | mod 4)'
         }

  rendered_data = render( data )

  assert rendered_data['x'] ==  Approx(1.2345)
  assert rendered_data['y'] ==  1
  assert rendered_data['z'] ==  2
  assert rendered_data['w'] ==  1
