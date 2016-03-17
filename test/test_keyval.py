import sys, os, timeit
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest
import utils
from configmakover.read import *
from configmakover.parsers import *

def test_quantity_support():

  text = '''
  zmin = 0 cm
  zmax = 1 m
  material/0/density = 988 kg/m^3
  material/0/thickness  = 10 um
  material/0/specheat = 4.182 kJ/kg/degK
  material/1/density = 1500 g/m^3
  material/1/thickness  = 2 mm
  material/1/specheat = 1 cal/g/degK
  '''

  spec = {
      'material/**/density': { 'unit' : 'g/cm^3', 'type' : 'mag' }
     ,'material/**/thickness': { 'unit' : 'cm', 'type' : 'mag' }
     ,'material/**/specheat': { 'unit' : 'J/g/degK', 'type' : 'mag' }
     ,'zmin' : {'unit': 'cm', 'type' : 'mag'}
     ,'zmax' : {'unit': 'cm', 'type' : 'mag'}
     }

  spec = '''
      'material/**/density':
        'unit' : 'g/cm^3'
        'type' : 'mag'
      'material/**/thickness':
        'unit' : 'cm'
        'type' : 'mag'
      'material/**/specheat':
        'unit' : 'J/g/degK'
        'type' : 'mag'
      'zmin' :
        'unit': 'cm'
        'type' : 'mag'
      'zmax' :
        'unit' : 'cm'
        'type' : 'mag'
        '''
  print yaml.load(spec)

  data = readConfig( text, parser=lambda x : keyval.load(x,separator='/'), spec=yaml.load(spec), return_DataTree=True )


  assert data['zmin'] == 0
  assert data['zmax'] == 100
  assert utils.close(data['material/0/density'], 988.*1000/100**3)
  assert utils.close(data['material/0/thickness'], 10e-6*100)
  assert utils.close(data['material/0/specheat'], 4.182)

  assert utils.close(data['material/1/density'], 1500./100**3)
  assert utils.close(data['material/1/thickness'], 0.2)
  assert utils.close(data['material/1/specheat'], 4.182)
