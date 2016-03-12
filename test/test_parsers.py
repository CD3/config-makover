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

def test_keyval_loader_nested():

  text = '''
  key1 = val1
  # comment
  key2 = 2.0
  key3 = 3 # comment

  key4 = 44

  level1/key1 = 11
  '''

  data = keyval.load( text )

  assert data['key1'] == 'val1'
  assert data['key2'] == '2.0'
  assert data['key3'] == '3'
  assert data['key4'] == '44'
  assert data['level1/key1'] == '11'


  data = keyval.load( text, separator='/' )

  assert data['key1'] == 'val1'
  assert data['key2'] == '2.0'
  assert data['key3'] == '3'
  assert data['key4'] == '44'
  assert data['level1']['key1'] == '11'

  with pytest.raises(RuntimeError):
    text += "key"
    data = keyval.load( text )

def test_keyval_dumper():

  data = { 'key1' : 1
         , 'key2' : 2.0
         , 'key3' : 'three'
         }

  text = keyval.dump( data )

  assert text == 'key1 = 1\nkey2 = 2.0\nkey3 = three\n'

def test_keyval_dumper_nested():

  data = { 'key1' : 1
         , 'key2' : 2.0
         , 'key3' : 'three'
         , 'level1' : { 'key11' : 11 }
         }

  text = keyval.dump( data )

  assert text == 'key1 = 1\nkey2 = 2.0\nkey3 = three\nlevel1/key11 = 11\n'
