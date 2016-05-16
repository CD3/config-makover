#! /usr/bin/python

import sys, os, timeit, pprint
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest

from configmakover.read import *
from configmakover.render import *

import utils

def test_simple():
  data = '''
  {{py:
import math
  }}
  var1 : 1
  var2 : some string
  var3 : 3
  var4 : "{{c['var3'] + math.pi + 2}}"
  var5 : "{{c['var4'] + 2.0}}"
  nest1 : &nest
    var1 : 11
    var2 : "{{c['var3'] + 12}}"
    var3 : "{{c['var1'] + 12}}"
    var4 : "{{c['var3'] + 12}}"
    var5 : "{{c['../nest1/var3'] + 12}}"
    list1 :
      - 01
      - "{{c['0']}}"
      - 03
    nest2 :
      var1 : 111
      var2 : 112
      var3 : "{{c['var1']}}"
      var4 : "{{c['/var1']}}"
      var5 : "{{c['/nest1/var1']}}"
  '''


  data = readConfig( data, render_filters=[toNum] )

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
  assert data['nest1']['list1'][0] == 1
  assert data['nest1']['list1'][1] == 1
  assert data['nest1']['list1'][2] == 3
  assert data['nest1']['nest2']['var1'] == 111
  assert data['nest1']['nest2']['var2'] == 112
  assert data['nest1']['nest2']['var3'] == 111
  assert data['nest1']['nest2']['var4'] == 1
  assert data['nest1']['nest2']['var5'] == 11

def test_large():
  data = '''
  {{py:
import math
  }}
  var1 : 1
  var2 : some string
  var3 : 3
  var4 : '{{c["var3"] + math.pi + 2}}'
  var5 : '{{c["var4"] + 2.0}}'
  nest1 : &nest
    var1 : 11
    var2 : '{{c["var3"] + 12}}'
    var3 : '{{c["var1"] + 12}}'
    var4 : '{{c["var3"] + 12}}'
    var5 : '{{c["../nest1/var3"] + 12}}'
    nest2 :
      var1 : 111
      var2 : 112
      var3 : '{{c["var1"]}}'
      var4 : '{{c["/var1"]}}'
      var5 : '{{c["/nest1/var1"]}}'
  nest2 :
    << : *nest
  nest3 :
    << : *nest
  nest4 :
    << : *nest
  nest5 :
    << : *nest
  nest6 :
    << : *nest
  nest7 :
    << : *nest
  nest8 :
    << : *nest
  nest9 :
    << : *nest
  nest10 :
    << : *nest
  '''


  data = readConfig( data, render_filters = [toNum] )

  assert data['var1'] == 1
  assert data['var2'] == 'some string'
  assert data['var3'] == 3
  assert utils.close( data['var4'], 3 + 3.14159 + 2 )
  assert utils.close( data['var5'], 3 + 3.14159 + 2 + 2.0 )
  assert data['nest10']['var1'] == 11
  assert data['nest10']['var2'] == 11 + 12 + 12
  assert data['nest10']['var3'] == 11 + 12
  assert data['nest10']['var4'] == 11 + 12 + 12
  assert data['nest10']['var5'] == 11 + 12 + 12
  assert data['nest10']['nest2']['var1'] == 111
  assert data['nest10']['nest2']['var2'] == 112
  assert data['nest10']['nest2']['var3'] == 111
  assert data['nest10']['nest2']['var4'] == 1
  assert data['nest10']['nest2']['var5'] == 11

def test_includes():
  nesteddata = { 'one' : 1, 'two' : 2 }

  data = r'''
  var1 : 1
  var2 : some string
  nest1 : include('example.yaml')
  nest2 : include('example.yaml')
  '''

  with open('example.yaml','w') as f:
    f.write(yaml.dump(nesteddata))

  data = readConfig( data, render_filters=[toNum] )

  assert data['nest1']['one'] == 1
  assert data['nest1']['two'] == 2
  assert data['nest2']['one'] == 1
  assert data['nest2']['two'] == 2

def test_datatable():

  with open('example-data.txt', 'w') as f:
    f.write('''
    # units: cm 1/cm
    1.0 4
    1.1 3
    1.2 2
    ''')

  data = r'''
  var1 : 1
  var2 : some string
  data : DataTable('example-data.txt')
  '''

  data = readConfig( data, render_filters=[toNum] )

  assert data['data'](0,0) == 1.0
  assert data['data'](0,1) == 4
  assert data['data'](1,0) == 1.1
  assert data['data'](1,1) == 3
  assert data['data'](2,0) == 1.2
  assert data['data'](2,1) == 2



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


  data = readConfig( data, render_filters=[toNum] )

  assert data['grid']['x']['min'] == 0
  assert data['grid']['x']['max'] == 10
  assert data['grid']['x']['N']   == 100
  assert data['grid']['y']['min'] == 0
  assert data['grid']['y']['max'] == 20
  assert data['grid']['y']['N']   == 200
  assert data['time']['start']    == 0
  assert data['time']['stop']     == 10
  assert data['time']['dt']       == 0.001

def test_physicsy():
  '''test a config typical of physics simulations'''
  data = '''
  # heat solver config file
  {{py:
import math
  }}
  res: 0.001
  grid:
    x:
      min : 0
      max : 10
      N   : '{{ (c["max",int] - c["min",int])/c["/res"] }}'
    y:
      min : 0
      max : '{{2*c["../x/max",float]}}'
      N   : '{{ (c["max",int] - c["min",int])/c["/res"] }}'
    z:
      min : 0
      max : '{{2*c["../y/max",float]}}'
      N   : '{{ (c["max",int] - c["min",int])/c["/res"] }}'
  time:
    start : 0
    stop : {{math.pow(10,2)}}
    dt : 0.001
  '''


  data = readConfig( data, render_filters=[toNum], return_DataTree=True )

  assert data['/grid/x/min'] == 0
  assert data['/grid/x/max'] == 10
  assert data['/grid/x/N']   == 10000
  assert data['/grid/y/min'] == 0
  assert data['/grid/y/max'] == 20
  assert data['/grid/y/N']   == 20000
  assert data['/grid/z/min'] == 0
  assert data['/grid/z/max'] == 40
  assert data['/grid/z/N']   == 40000
  assert data['/time/start'] == 0
  assert data['/time/stop']  == 100
  assert data['/time/dt']    == 0.001

def test_datatable2():
  with open('abscoe-data.txt', 'w') as f:
    f.write('''
    # units: nm 1/cm
    400 100
    450 200
    500 300
    550 400
    600 500
    650 600
    700 700
    750 800
    ''')

  data = '''
  {{py:
import math
  }}
  res: 0.001
  wavelength : 500
  grid:
    x:
      min : 0
      max : 10
      N   : '{{ (c["max",int] - c["min",int])/c["/res"] }}'
  time:
    start : 0
    stop : {{math.pow(10,2)}}
    dt : 0.001
  materials :
    - desc : 'absorbing material'
      abscoe_data : DataTable('abscoe-data.txt')
      abscoe :
        - "{{ c['/wavelength']+" "+c['../abscoe_data'].iget( Q_(c['/wavelength']), unit='1/m') }}"
  '''

  data = readConfig( data, return_DataTree=True )

  # pprint.pprint(data.data)


  assert utils.close( data['/materials/0/abscoe/0'].magnitude, 300*100 )
