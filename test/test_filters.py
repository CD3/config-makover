#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *

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

  data = readConfig( text, filters=filter_on_layer )
  print data

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


  data = readConfig( text, filters=[set_type,plus_one] )
  print data


def test_list_generation():
  text = '''
  var : 1,2,3
  nest :
    var : 4,5,6
    nest :
      var : 7,8,9
  '''

  def expand_range( val ):
    if isinstance(val,dict) or isinstance(val,list):
      return val

    try:
      if isinstance(val, unicode):
        val = str(val)

      if isinstance(val, str):
        if val.find(',') > -1:
          val = val.strip().split(',')
      else:
        val = float(val)

    except:
      return val
    
    return val


  data = readConfig( text, filters=expand_range )

  print data

