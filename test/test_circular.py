#! /usr/bin/python

import sys, os, json
import pytest
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *

import utils

#logging.basicConfig(level=logging.DEBUG)

@pytest.mark.xfail
def test_circular_deps():
  with pytest.raises(NameError):
    data = '''
    var1 : 1
    var2 : {{var3}}
    var3 : {{var2}}
    nest1 :
      var1 : 11
      var2 : 12
      nest2 :
        var1 : 111
        var2 : 112
    '''

    data = readConfig( data )



