#! /usr/bin/python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest

from configmakover.render import *

import utils
#logging.basicConfig( level=logging.DEBUG )

def test_renderTree_simple():
  data = { 'one' : 1
          ,'two' : 2
          ,'three': '{{one}}'
          ,'four' : '{{one + two}}'
          ,'level1' : { 'one' : 11
                       ,'two' : 12
                       ,'three': '{{one}}'
                       ,'four' : '{{one + two}}'
                      }
         }
  rendered_data = renderTree( data )

  assert rendered_data['three'] == 1
  assert rendered_data['four']  == 3
  assert rendered_data['level1']['three'] == 1
  assert rendered_data['level1']['four']  == 3

def test_renderTree_missing_var():
  data = { 'one' : 1
          ,'two' : 2
          ,'three': '{{one}}'
          ,'four' : '{{one + two}}'
          ,'five' : '{{missing}}'
          ,'level1' : { 'one' : 11
                       ,'two' : 12
                       ,'three': '{{one}}'
                       ,'four' : '{{one + two}}'
                       ,'five' : '{{one + two}}'
                      }
         }
  rendered_data = renderTree( data )

  assert rendered_data['three'] == 1
  assert rendered_data['four']  == 3
  assert rendered_data['level1']['three'] == 1
  assert rendered_data['level1']['four']  == 3

def test_renderTree_imports():
  # test that we can import modules that are needed for rendering
  data = { 'var1' : '{{math.sqrt(2)}}'
          ,'var2' : '{{numpy.sqrt(2)}}'
          ,'var3' : '{{var1 + math.pi}}'
         }
  rendered_data = renderTree( data, imports = ['math','numpy'] )

  import math, numpy
  assert utils.close( rendered_data['var1'], math.sqrt(2)  )
  assert utils.close( rendered_data['var2'], numpy.sqrt(2) )
  assert utils.close( rendered_data['var3'], math.sqrt(2) + math.pi )


def test_renderTree_throw_on_undefined():
  data = { 'var1' : '{{missing}}' }

  with pytest.raises(RuntimeError):
    rendered_data = renderTree( data , strict=True )

def test_renderTree_multi_ref():
  data = { 'one' : 1
          ,'two' : '{{one}}'
          ,'three': '{{two}}'
          ,'four': '{{three}}'
          ,'five' : '{{one + 1}}'
          ,'six': '{{two + 1}}'
         }
  rendered_data = renderTree( data )

  assert rendered_data['two'] == 1
  assert rendered_data['three']  == 1
  assert rendered_data['four'] == 1
  assert rendered_data['five']  == 2
  assert rendered_data['six']  == 2


def test_scopedRenderTree_simple():
  data = { 'one' : 1
          ,'two' : 2
          ,'three': '{{one}}'
          ,'four' : '{{one + two}}'
          ,'level1' : { 'one' : 11
                       ,'two' : 12
                       ,'three': '{{one}}'
                       ,'four' : '{{one + two}}'
                      }
         }
  rendered_data = scopedRenderTree( data )

  assert rendered_data['three'] == 1
  assert rendered_data['four']  == 3
  assert rendered_data['level1']['three'] == 11
  assert rendered_data['level1']['four']  == 23

def test_scopedRenderTree_multi_ref():
  data = { 'one' : 1
          ,'two' : '{{one}}'
          ,'three': '{{two}}'
          ,'four': '{{three}}'
          ,'five' : '{{one + 1}}'
          ,'six': '{{two + 1}}'
         }
  rendered_data = scopedRenderTree( data )

  assert rendered_data['two'] == 1
  assert rendered_data['three']  == 1
  assert rendered_data['four'] == 1
  assert rendered_data['five']  == 2
  assert rendered_data['six']  == 2




def test_renderDictTree_simple():
  data = { 'one' : 1
          ,'two' : 2
          ,'three': "{{l('one')}}"
          ,'@three_type': "int"
          ,'four' : "{{l('one') + l('two')}}"
          ,'@four_type': "int"
          ,'level1' : { 'one' : 11
                       ,'two' : 12
                       ,'three': '{{l("one")}}'
                       ,'@three_type': "int"
                       ,'four' : '{{l("one") + l("two")}}'
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


# def test_renderDictTree_throw_on_undefined():
  # data = { 'var1' : '{{missing}}' }

  # with pytest.raises(RuntimeError):
    # rendered_data = renderTree( data , strict=True )

# def test_renderDictTree_multi_ref():
  # data = { 'one' : 1
          # ,'two' : '{{one}}'
          # ,'three': '{{two}}'
          # ,'four': '{{three}}'
          # ,'five' : '{{one + 1}}'
          # ,'six': '{{two + 1}}'
         # }
  # rendered_data = renderTree( data )

  # assert rendered_data['two'] == 1
  # assert rendered_data['three']  == 1
  # assert rendered_data['four'] == 1
  # assert rendered_data['five']  == 2
  # assert rendered_data['six']  == 2

