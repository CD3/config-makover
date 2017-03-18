
import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

import pytest
from utils import *


from dynconfig.render import *

def test_simple():
  logging.info("exceptions")

  with pytest.raises(RuntimeError) as e:
    rendered_data = render( {'one':1, 'two':"$(one)"}, strict=True )

