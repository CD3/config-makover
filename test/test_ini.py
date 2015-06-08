#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *
from configmakover.parsers import ini

import utils
#logging.basicConfig( level=logging.DEBUG )

def test_simple():
  data = '''
<%!
import math
%>
[main]
var1 = 1
var2 = some string
var3 = 3
var4 = ${var3 + math.pi + 2}
var5 = ${var4 + 2.0}
[nest1]
var1 = 11
var2 = ${var3 + 12}
var3 = ${var1 + 12}
var4 = ${var3 + 12}
var5 = ${nest1.var3 + 12}
'''

  def num(x,y):
    print y
    try:
      return float(x)
    except:
      return x

  data = readConfig( data, parser = ini.load, filters = num )

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

