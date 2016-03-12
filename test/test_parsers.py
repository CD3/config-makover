import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest

from configmakover.parsers import *

import utils

def test_keyval_loader():

  text = '''
  key1 = val1
  # comment
  key2 = 2.0
  key3 = 3 # comment

  key4 = 44
  '''

  data = keyval.load( text )

  assert data['key1'] == 'val1'
  assert data['key2'] == '2.0'
  assert data['key3'] == '3'
  assert data['key4'] == '44'

  with pytest.raises(RuntimeError):
    text += "key"
    data = keyval.load( text )

def test_keyval_loader():

  data = { 'key1' : 1
         , 'key2' : 2.0
         , 'key3' : 'three'
         }

  text = keyval.dump( data )

  assert text == 'key1 = 1\nkey2 = 2.0\nkey3 = three\n'

