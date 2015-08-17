import sys, os, timeit
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest

from configmakover.read import *
from configmakover.render import *

import utils

def test_chained_references_performance():

  data = dict()

  data["v0"] = 10
  for i in range(1,40):
    data["v%s"%str(i)] = "{{l.v%s + 1}}"%(i-1)

  print

  timer = timeit.Timer( lambda: renderDictTree(data) )
  print timer.timeit(1)


def test_reversed_chained_references_performance():

  data = dict()

  data["v40"] = 10
  for i in range(0,40):
    data["v%s"%str(i)] = "{{l.v%s + 1}}"%(i+1)

  print

  timer = timeit.Timer( lambda: renderDictTree(data) )
  print timer.timeit(1)

