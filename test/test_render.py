#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest

from configmakover.render import *
from configmakover.DataTree import *

import utils
#logging.basicConfig( level=logging.DEBUG )

def test_renderDictTree_simple():
  data = { 'one' : 1
          ,'two' : 2
          ,'three': "{{l('one')}}"
          ,'@three_type': "int"
          ,'four' : "{{l.one + l.two}}"
          ,'@four_type': "int"
          ,'level1' : { 'one' : 11
                       ,'two' : 12
                       ,'three': '{{l("one")}}'
                       ,'@three_type': "int"
                       ,'four' : '{{l.one + l.two}}'
                       ,'@four_type': "int"
                      }
         }
  rendered_data = renderDictTree( data )

  assert rendered_data['three'] == 1
  assert rendered_data['four']  == 3
  assert rendered_data['level1']['three'] == 11
  assert rendered_data['level1']['four']  == 11 + 12

def test_renderDictTree_missing_var():
  data = { 'one' : 1
          ,'two' : 2
          ,'three': '{{l("one")}}'
          ,'@three_type': "int"
          ,'four' : '{{l("one") + l("two")}}'
          ,'@four_type': "int"
          ,'five' : '{{l("missing")}}'
          ,'level1' : { 'one' : 11
                       ,'two' : 12
                       ,'three': '{{l("one")}}'
                       ,'@three_type': "int"
                       ,'four' : '{{l("one") + l("two")}}'
                       ,'@four_type': "int"
                       ,'five' : '{{l("one") + l("two")}}'
                      }
         }
  rendered_data = renderDictTree( data )

  assert rendered_data['three'] == 1
  assert rendered_data['four']  == 3
  assert rendered_data['level1']['three'] == 11
  assert rendered_data['level1']['four']  == 11 + 12

def test_renderDictTree_imports():
  # test that we can import modules that are needed for rendering
  data = { 'var1' : '{{math.sqrt(2)}}'
          ,'var2' : '{{numpy.sqrt(2)}}'
          ,'var3' : '{{l("var1") + math.pi}}'
         }
  rendered_data = renderDictTree( data, imports = ['math','numpy'] )

  import math, numpy
  assert utils.close( rendered_data['var1'], math.sqrt(2)  )
  assert utils.close( rendered_data['var2'], numpy.sqrt(2) )
  assert utils.close( rendered_data['var3'], math.sqrt(2) + math.pi )


def test_renderDictTree_throw_on_undefined():
  data = { 'var1' : '{{missing}}' }

  with pytest.raises(RuntimeError):
    rendered_data = renderDictTree( data , strict=True )

def test_renderDictTree_multi_ref():
  data = { 'one' : 1
          ,'two' : '{{l("one")}}'
          ,'three': '{{l("two")}}'
          ,'four': '{{l("three")}}'
          ,'five' : '{{l("one") + 1}}'
          ,'six': '{{l("two") + 1}}'
          ,'seven': '{{l("six") + 1}}'
         }
  rendered_data = renderDictTree( data )

  assert rendered_data['two'] == 1
  assert rendered_data['three']  == 1
  assert rendered_data['four'] == 1
  assert rendered_data['five']  == 2
  assert rendered_data['six']  == 2
  assert rendered_data['seven']  == 3

def test_renderDataTree():
  data = DataTree({ 'one' : 1
                   ,'two' : 2
                   ,'three': "{{c['one']}}"
                   ,'four' : "{{c['one'] + c['two']}}"
                   ,'level1' : { 'one' : 11
                                ,'two' : 12
                                ,'three': '{{c["one"]}}'
                                ,'four' : '{{c["one"] + c["two"]}}'
                               }
                  } )
  rendered_data = renderDataTree( data )

  assert rendered_data['three'] == str(1)
  assert rendered_data['four']  == str(3)
  assert rendered_data['level1']['three'] == str(11)
  assert rendered_data['level1']['four']  == str(11 + 12)

def test_renderDataTree_multi_ref():

  data = DataTree({ 'one' : '1'
                   ,'two' : '2'
                   ,'three': "{{c['one']}}"
                   ,'four' : "{{c['one'] + c['two']}}"
                   ,'five' : "{{c['four']}}"
                   ,'six'  : "{{c['three',float] + c['four',float]}}"
                  } )
  for p in data.get_tippaths():
    data.set_spec( data._join(p,'type'), 'float' )

  rendered_data = renderDataTree( data )

  assert rendered_data['one']   == 1
  assert rendered_data['two']   == 2
  assert rendered_data['three'] == 1
  assert rendered_data['four']  == 3
  assert rendered_data['five']  == 3
  assert rendered_data['six']   == 4

