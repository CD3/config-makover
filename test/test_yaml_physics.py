#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *

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


#data = readConfig( data )
#print yaml.dump(data, default_flow_style=False)


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
  stop : 10
  dt : 0.001
'''


data = readConfig( data )
print yaml.dump(data, default_flow_style=False)
