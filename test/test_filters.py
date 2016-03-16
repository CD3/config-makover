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
    if len( key.split('/') ) % 2 == 0:
      return float(str(val))
    else:
      return str(val)

    return val

  data = readConfig( text, post_filters=[filter_on_layer] )
  # logging.debug( "RESULT" )
  # logging.debug( data )

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
    if key.endswith('num'):
      return int(val)
    
    if key.endswith('str'):
      return str(val)

    return val

  def plus_one( val ):
    try:
      if val < 3.5:
        return val + 1
    except:
      return val
    
    return val


  data = readConfig( text, post_filters=[set_type,plus_one] )
  # logging.debug( "RESULT" )
  # logging.debug( data )

  assert isinstance(data['num'], int)
  assert            data['num'] == 2

  assert isinstance(data['nest']['str'], str)
  assert            data['nest']['str'] == '2'

  assert isinstance(data['nest']['nest']['num'], int)
  assert            data['nest']['nest']['num'] == 4

  assert isinstance(data['nest']['nest']['nest']['str'], str)
  assert            data['nest']['nest']['nest']['str'] == '4'

  assert isinstance(data['nest']['nest']['nest']['nest']['num'], int)
  assert            data['nest']['nest']['nest']['nest']['num'] == 5

  assert isinstance(data['nest']['nest']['nest']['nest']['nest']['str'], str)
  assert            data['nest']['nest']['nest']['nest']['nest']['str'] == '6'


def test_list_generation():
  text = '''
  var : 1,2,3
  nest :
    var : 4,5,6
    nest :
      var : 7,8,9
  '''

  data = readConfig( text, post_filters=[expand_list])

  assert isinstance( data, dict)
  assert isinstance( data['var'], list)
  assert isinstance( data['nest'], dict)
  assert isinstance( data['nest']['var'], list)
  assert isinstance( data['nest']['nest'], dict)
  assert isinstance( data['nest']['nest']['var'], list)
  
  assert data['var'][0] == '1'
  assert data['var'][1] == '2'
  assert data['var'][2] == '3'
  assert data['nest']['var'][0] == '4'
  assert data['nest']['var'][1] == '5'
  assert data['nest']['var'][2] == '6'
  assert data['nest']['nest']['var'][0] == '7'
  assert data['nest']['nest']['var'][1] == '8'
  assert data['nest']['nest']['var'][2] == '9'

  data = readConfig( text, post_filters=[expand_list,lambda x : int(x)])

  assert isinstance( data, dict)
  assert isinstance( data['var'], list)
  assert isinstance( data['nest'], dict)
  assert isinstance( data['nest']['var'], list)
  assert isinstance( data['nest']['nest'], dict)
  assert isinstance( data['nest']['nest']['var'], list)
  
  assert data['var'][0] == 1
  assert data['var'][1] == 2
  assert data['var'][2] == 3
  assert data['nest']['var'][0] == 4
  assert data['nest']['var'][1] == 5
  assert data['nest']['var'][2] == 6
  assert data['nest']['nest']['var'][0] == 7
  assert data['nest']['nest']['var'][1] == 8
  assert data['nest']['nest']['var'][2] == 9

def test_none_filters():
  text = '''
  var : 1
  nest :
    var : 2
    nest :
      var : 3
  '''


  data = readConfig( text, render_filters=None)

  # logging.debug( "RESULT" )
  # logging.debug( data )

  assert data['var'] == 1
  assert data['nest']['var'] == 2
  assert data['nest']['nest']['var'] == 3

