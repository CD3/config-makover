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
'''


data = readConfig( data )
print yaml.dump(data, default_flow_style=False)



#data = { 'one' : { 'one' : { 'one' : 111, 'two' : 112 }, 'two' : 12 }, 'two' : 2, 'three' : [ 1, 2, {'one' : 333} ] }

#data = toAttrDict(data)

#print data.one.one.one
#print data.three[2].one
