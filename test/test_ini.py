#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import ConfigParser, StringIO
from configmakover.read import *
from configmakover.parsers import ini

import utils
#logging.basicConfig( level=logging.DEBUG )

def test_simple():
  data = '''
{{py:
import math, numpy
}}
[main]
var1 = 1
var2 = some string
var3 = 3
var4 = {{l.var3 + math.pi + 2}}
var5 = {{l.var4 + 2.0}}
[nest1]
var1 = 11
var2 = {{l.var3 + 12}}
var3 = {{l.var1 + 12}}
var4 = {{l.var3 + 12}}
var5 = {{g.nest1.var3 + 12}}
'''

  data = readConfig( data, parser = ini.load, render_filters = toNum )

  assert data['main']['var1'] == 1
  assert data['main']['var2'] == 'some string'
  assert data['main']['var3'] == 3
  assert utils.close( data['main']['var4'], 3 + 3.14159 + 2 )
  assert utils.close( data['main']['var5'], 3 + 3.14159 + 2 + 2.0 )
  assert data['nest1']['var1'] == 11
  assert data['nest1']['var2'] == 11 + 12 + 12
  assert data['nest1']['var3'] == 11 + 12
  assert data['nest1']['var4'] == 11 + 12 + 12
  assert data['nest1']['var5'] == 11 + 12 + 12

def test_configParser():
  '''A vanilla configparser example'''
  text= '''
[main]
var1 = 1
var2 = some string
var3 = 3
var4 = %(var3)s
var5 = %(var4)s
[nest1]
var1 = 11
var2 = %(var3)s
var3 = %(var1)s
var4 = %(var3)s
#var5 = %(main.var3)s # this will cause an interpolation error
'''

  parser = ConfigParser.ConfigParser()
  f = StringIO.StringIO(text)
  parser.readfp( f )
  f.close()

  data = dict()
  for sec in parser.sections():
    data[sec] = dict()
    for opt in parser.options(sec):
      data[sec][opt] = parser.get( sec, opt )

