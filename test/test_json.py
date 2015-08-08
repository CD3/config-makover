#! /usr/bin/python

import sys, os, json
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *

import utils

#logging.basicConfig(level=logging.DEBUG)

def test_simple():
  data = '''
{
{{py:
import math
}}
"var1" : 1,
"var2" : "some string",
"var3" : 3,
"var4" : "{{var3 + math.pi + 2}}",
"var5" : "{{var4 + 2.0}}",
"nest1" : {
  "var1" : 11,
  "var2" : "{{var3 + 12}}",
  "var3" : "{{var1 + 12}}",
  "var4" : "{{var3 + 12}}",
  "var5" : "{{nest1.var3 + 12}}",
  "nest2" : {
    "var1" : 111,
    "var2" : 112,
    "var3" : "{{var1}}",
    "var4" : "{{top.var1}}",
    "var5" : "{{nest1.var1}}"
    }
  }
}
  '''

  data = readConfig( data, parser=json.loads, render_filters = toNum )

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


