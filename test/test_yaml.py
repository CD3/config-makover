#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *

scheme = '''
'''

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
  var5 : ${nest1['var3'] + 12}
  nest2 :
    var1 : 111
    var2 : 112
    var3 : ${var1}
    var4 : ${top.var1}
'''


data = readConfig( data )
print yaml.dump(data, default_flow_style=False)



