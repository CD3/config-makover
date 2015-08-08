#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest

from configmakover.read import *
from configmakover.filters import *

import utils
#logging.basicConfig( level=logging.DEBUG )

def test_level_filter():
  text = '''
  var : 1
  nest :
    var : 2
    nest :
      var : 3
      nest :
        var : 4
        nest :
          var : 5
          nest :
            var : 6
  '''

  def filter_on_layer( val, key ):
    if not isinstance(val, dict):
      if len( key.split('.') ) % 2 == 0:
        return str(val)
      else:
        return float(str(val))

    return val

  data = readConfig( text, render_filters=filter_on_layer )
  logging.debug( "RESULT" )
  logging.debug( data )

  assert isinstance( data['var'], str)
  assert isinstance( data['nest']['var'], float)
  assert isinstance( data['nest']['nest']['var'], str)
  assert isinstance( data['nest']['nest']['nest']['var'], float)
  assert isinstance( data['nest']['nest']['nest']['nest']['var'], str)
  assert isinstance( data['nest']['nest']['nest']['nest']['nest']['var'], float)


def test_multiple_filters():
  text = '''
  num : 1
  nest :
    str : 2
    nest :
      num: 3
      nest :
        str: 4
        nest :
          num: 5
          nest :
            str: 6
  '''

  def set_type( val, key ):
    if isinstance( val, dict ):
      return val
    
    if isinstance( val, list ):
      return val

    if isinstance(val,unicode):
      val = str(val)

    if key == 'num' and isinstance(val,str):
      return float(val)
    
    if key == 'str':
      return str(val)

    return val

  def plus_one( val ):
    try:
      if val < 10:
        return val + 1
    except:
      return val
    
    return val


  data = readConfig( text, render_filters=[set_type,plus_one] )
  logging.debug( "RESULT" )
  logging.debug( data )


def test_list_generation():
  text = '''
  var : 1,2,3
  nest :
    var : 4,5,6
    nest :
      var : 7,8,9
  '''

  data = readConfig( text, render_filters=expand_list)

  logging.debug( "RESULT" )
  logging.debug( data )


  assert isinstance( data, dict)
  assert isinstance( data['var'], list)
  assert isinstance( data['nest'], dict)
  assert isinstance( data['nest']['var'], list)
  assert isinstance( data['nest']['nest'], dict)
  assert isinstance( data['nest']['nest']['var'], list)

def test_none_filters():
  text = '''
  var : 1
  nest :
    var : 2
    nest :
      var : 3
  '''


  data = readConfig( text, render_filters=None )

  logging.debug( "RESULT" )
  logging.debug( data )

  assert data['var'] == 1
  assert data['nest']['var'] == 2
  assert data['nest']['nest']['var'] == 3

def test_pre_post_filters():
  text = '''
  var1 : '1'
  var2 : '{{var1 + 1}}'
  nest :
    var1 : '2'
    var2 : '{{var1 + 1}}'
    nest :
      var1 : '3'
      var2 : '{{var1 + 1}}'
  '''


  def num(val):
    if isContainer(val):
      return val

    try:
      return float(val)
    except:
      return val


  with pytest.raises(RuntimeError):
    data = readConfig( text , render_filters=None)

  data = readConfig( text , pre_filters=num, render_filters=None)

  logging.debug( "RESULT" )
  logging.debug( data )

  assert data['var1'] == 1
  assert data['var2'] == '2.0'
  assert data['nest']['var1'] == 2
  assert data['nest']['var2'] == '3.0'
  assert data['nest']['nest']['var1'] == 3
  assert data['nest']['nest']['var2'] == '4.0'



  data = readConfig( text , pre_filters=num, post_filters=num, render_filters=None)

  logging.debug( "RESULT" )
  logging.debug( data )

  assert data['var1'] == 1
  assert data['var2'] == 2
  assert data['nest']['var1'] == 2
  assert data['nest']['var2'] == 3
  assert data['nest']['nest']['var1'] == 3
  assert data['nest']['nest']['var2'] == 4




