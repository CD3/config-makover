#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest
from utils import *


from dynconfig.render import *
from dynconfig.utils import *

def test_simple():
  logging.info("simple quantities")
  data = { 'size' : 100
          ,'x':
          { 'min' : "$( '-1 m' | to cm | float)"
          , 'max' : "$( '2 m' | to cm | float )"
          , 'dx'  : '$( ({max} - {min}) / {/size} )'
          }
          ,'pulse-width' : "$(10 us | to s | float)"
         }

  rendered_data = render( data, repeat = True )

  assert type(rendered_data['x']['dx']) ==  float
  assert rendered_data['x']['dx'] ==  Approx( (200.-(-100.))/100 )

  assert type(rendered_data['pulse-width']) ==  float
  assert rendered_data['pulse-width'] ==  Approx(10e-6)

def test_full_quantity_support():

  logging.info("full quantity support")
  data = { 'distance' : "$( 100 mile | q )"
          ,'time' : "$( 1 hour | q )"
          ,'velocity' : "$({distance}/{time} | to m/s)"
         }

  rendered_data = render( data, repeat = True )

  assert str(rendered_data['distance']) == '100 mile'
  assert rendered_data['distance'].magnitude == Approx(100)
  assert str(rendered_data['distance'].units) == 'mile'
  assert str(rendered_data['distance'].to('km')) == '160.9344 kilometer'

  assert rendered_data['time'].magnitude == Approx(1)
  assert str(rendered_data['time'].units) == 'hour'

  assert rendered_data['velocity'].magnitude == Approx(44.704)
  assert str(rendered_data['velocity'].units) == 'meter / second'

  transform(rendered_data, lambda q : q.magnitude)

  assert rendered_data['distance'] == Approx(100)
  assert rendered_data['time'] == Approx(1)
  assert rendered_data['velocity'] == Approx(44.704)


