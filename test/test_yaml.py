#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *

import utils


def test_simple():
  data = '''
  <%!
    import math
  %>
  var1 : 1
  var2 : some string
  var3 : 3
  var4 : ${var3 + math.pi + 2}
  var5 : ${var4 + 2.0}
  nest1 :
    var1 : 11
    var2 : ${var3 + 12}
    var3 : ${var1 + 12}
    var4 : ${var3 + 12}
    var5 : ${nest1.var3 + 12}
    nest2 :
      var1 : 111
      var2 : 112
      var3 : ${var1}
      var4 : ${top.var1}
      var5 : ${nest1.var1}
  '''


  data = readConfig( data )

  assert data['var1'] == 1
  assert data['var2'] == 'some string'
  assert data['var3'] == 3
  assert utils.close( data['var4'], 3 + 3.14159 + 2 )
  assert utils.close( data['var5'], 3 + 3.14159 + 2 + 2.0 )
  assert data['nest1']['var1'] == 11
  assert data['nest1']['var2'] == 11 + 12 + 12
  assert data['nest1']['var3'] == 11 + 12
  assert data['nest1']['var4'] == 11 + 12 + 12
  assert data['nest1']['var5'] == 11 + 12 + 12
  assert data['nest1']['nest2']['var1'] == 111
  assert data['nest1']['nest2']['var2'] == 112
  assert data['nest1']['nest2']['var3'] == 111
  assert data['nest1']['nest2']['var4'] == 1
  assert data['nest1']['nest2']['var5'] == 11


def test_passthrough():
  '''test that a config file containing no template expressions works'''

  data = '''
  # heat solver config file
  grid:
    x:
      min : 0
      max : 10
      N   : 100
    y:
      min : 0
      max : 20
      N   : 200
  time:
    start : 0
    stop : 10
    dt : 0.001
  '''


  data = toAttrDict( readConfig( data ) )

  assert data.grid.x.min == 0
  assert data.grid.x.max == 10
  assert data.grid.x.N   == 100
  assert data.grid.y.min == 0
  assert data.grid.y.max == 20
  assert data.grid.y.N   == 200
  assert data.time.start == 0
  assert data.time.stop  == 10
  assert data.time.dt    == 0.001


def test_physicsy():
  '''test a config typical of physics simulations'''
  data = '''
  # heat solver config file
  <%!
    import math
    res = 0.001
  %>
  grid:
    x:
      min : 0
      max : 10
      N   : ${int( (max - min)/res )}
    y:
      min : 0
      max : ${2*x.max}
      N   : ${int( (max - min)/res )}
  time:
    start : 0
    stop : ${math.pow(10,2)}
    dt : 0.001
  '''


  data = toAttrDict( readConfig( data ) )

  assert data.grid.x.min == 0
  assert data.grid.x.max == 10
  assert data.grid.x.N   == 10000
  assert data.grid.y.min == 0
  assert data.grid.y.max == 20
  assert data.grid.y.N   == 20000
  assert data.time.start == 0
  assert data.time.stop  == 100
  assert data.time.dt    == 0.001

