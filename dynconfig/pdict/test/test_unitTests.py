import pytest,pprint
from pdict import pdict

def test_interface():
  d = pdict()

  d['type'] = 'plain'
  d['grid'] = pdict()
  d['grid']['dimensions'] = 2
  d['grid']['x'] = pdict()
  d['grid']['x']['min'] = 0
  d['grid']['x']['max'] = 2.5
  d['grid']['x']['n'] = 100
  d['grid']['y'] = { 'min' : -1, 'max' : 1, 'n' : 200 }
  d['time'] = { 'stepper' : { 'type' : 'uniform', 'tolerance' : {'min' : 1e-5, 'max' : 1e-4} } }
  d['search'] = { 'method' : 'bisection', 'range' : [0, 100] }
  d['sources'] = [ {'type' : 'laser'}, {'type' : 'RF' } ]


  assert d['type'] == "plain"
  assert d['grid']['dimensions'] == 2
  assert d['grid']['x']['min'] == 0
  assert d['grid']['x']['max'] == 2.5
  assert d['grid']['x']['n'] == 100
  assert d['grid']['y']['min'] == -1
  assert d['grid']['y']['max'] == 1
  assert d['grid']['y']['n'] == 200
  assert d['time']['stepper']['type'] == "uniform"
  assert d['time']['stepper']['tolerance']['min'] == 1e-5
  assert d['time']['stepper']['tolerance']['max'] == 1e-4
  assert d['search']['method'] == 'bisection'
  assert d['search']['range'][0] == 0
  assert d['search']['range']['1'] == 100
  assert d['sources'][0]['type'] == 'laser'
  assert d['sources'][1]['type'] == 'RF'

  assert d['type'] == "plain"
  assert d['grid/dimensions'] == 2
  assert d['grid/x/min'] == 0
  assert d['grid/x/max'] == 2.5
  assert d['grid/x/n'] == 100
  assert d['grid/y/min'] == -1
  assert d['grid/y/max'] == 1
  assert d['grid/y/n'] == 200
  assert d['time/stepper/type'] == "uniform"
  assert d['time/stepper/tolerance/min'] == 1e-5
  assert d['time/stepper/tolerance/max'] == 1e-4
  assert d['search/method'] == 'bisection'
  assert d['search/range/0'] == 0
  assert d['search/range/1'] == 100
  assert d['sources/0/type'] == 'laser'
  assert d['sources/1/type'] == 'RF'

  assert d['grid/x/min'] == 0
  assert d['grid/x/max'] == 2.5
  assert d['grid/x/n'] == 100

  assert d['grid/x']['../dimensions'] == 2

  assert d['grid/x']['../y/min'] == -1
  assert d['grid/x']['../y/max'] == 1
  assert d['grid/x']['../y/n'] == 200
  assert d['grid/x']['/type'] == "plain"
  assert d['grid/x']['/grid/y/min'] == -1
  assert d['grid/x']['/grid/y/max'] == 1
  assert d['grid/x']['/grid/y/n'] == 200

  d = pdict()
  d.update( {'grid' : { 'x' : { 'min' : 0, 'max' : 1, 'n' : 100 } } } )

  assert d['grid']['x']['min'] == 0
  assert d['grid']['x']['max'] == 1
  assert d['grid']['x']['n'] == 100

  assert d['grid/x/min'] == 0
  assert d['grid/x/max'] == 1
  assert d['grid/x/n'] == 100

  d = pdict()
  d['grid/x/min'] = 0
  d['grid/x']['max'] = 1
  d['grid/x']['/grid/x/n'] = 100
  d['grid/x']['/type'] = "sim"

  assert d['grid']['x']['min'] == 0
  assert d['grid']['x']['max'] == 1
  assert d['grid']['x']['n'] == 100
  assert d['type'] == 'sim'


def test_dict_conversions():
  d = pdict()
  d.update( { 'a' : { 'b' : { 'c' : { 'd' : 0 }, 'e' : [ 0, 1, 2, [10, 11, 12] ] } } } )

  assert d['a/b/c/d'] == 0
  assert d['a/b/e/0'] == 0
  assert d['a/b/e/1'] == 1
  assert d['a/b/e/2'] == 2
  assert d['a/b/e/3/0'] == 10

  assert type(d) == pdict
  assert type(d['a']) == pdict
  assert type(d['a/b']) == pdict
  assert type(d['a/b/c']) == pdict
  assert type(d['a/b/c/d']) == int
  assert type(d['a/b/e']) == pdict
  assert type(d['a/b/e/0']) == int
  assert type(d['a/b/e/3']) == pdict
  assert type(d['a/b/e/3/0']) == int

  dd = d.dict()

  assert dd['a']['b']['c']['d'] == 0
  assert dd['a']['b']['e'][0] == 0
  assert dd['a']['b']['e'][1] == 1
  assert dd['a']['b']['e'][2] == 2
  assert dd['a']['b']['e'][3][0] == 10

  assert type(dd) == dict
  assert type(dd['a']) == dict
  assert type(dd['a']['b']) == dict
  assert type(dd['a']['b']['c']) == dict
  assert type(dd['a']['b']['c']['d']) == int
  assert type(dd['a']['b']['e']) == list
  assert type(dd['a']['b']['e'][0]) == int
  assert type(dd['a']['b']['e'][3]) == list
  assert type(dd['a']['b']['e'][3][0]) == int


def test_paths():
  d = pdict()

  d.update( { 'type':'sim', 'grid' : { 'x' : { 'min' : 0, 'max' : 10, 'n' : 100 } } } )

  assert d['grid']['x'].path() == '/grid/x'
  assert d['grid']['x']['..'].path() == '/grid'
  assert d['grid']['x']['../'].path() == '/grid'
  assert d['grid']['x']['../../grid'].path() == '/grid'

  assert d['grid']['/.'] == d
  assert d['grid']['/'] == d

  assert d.pathname("grid/x") == 'grid'
  assert d.pathname("/grid/x") == '/grid'
  assert d.pathname("x") == ''
  assert d.pathname("/x") == '/'

  assert d.basename("grid/x") == 'x'
  assert d.basename("/grid/x") == 'x'
  assert d.basename("x") == 'x'
  assert d.basename("/x") == 'x'
