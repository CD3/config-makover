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
    data["v%s"%str(i)] = "{{c['v%s',int] + 1}}"%(i-1)

  print

  timer = timeit.Timer( lambda: renderDictTree(data) )
  print timer.timeit(1)
  applyFiltersToDict( data, [lambda x : int(x)] )

  for i in range(0,40):
    assert data["v%s"%str(i)] == 10+i


def test_reversed_chained_references_performance():

  data = dict()

  data["v40"] = 10
  for i in range(0,40):
    data["v%s"%str(i)] = "{{c['v%s',int] + 1}}"%(i+1)

  print

  timer = timeit.Timer( lambda: renderDictTree(data) )
  print timer.timeit(1)
  applyFiltersToDict( data, [lambda x : int(x)] )

  for i in range(0,41):
    # v40 == 10
    # v39 == 11
    # ...
    assert data["v%s"%str(i)] == 10+(40-i)

