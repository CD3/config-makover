
import cerberus
import dpath.util
from collections import Sequence, Mapping
import copy

from .render import *

class Validator(cerberus.Validator):
  def __init__(self, *args, **kargs):
    super(Validator,self).__init__(*args, **kargs)

    self.current_path = []

  def _validate_test(self, args, field, value):
    print 
    print "DOC", self.document
    print "PATH",self.current_path
    print "SCHEMA", self.schema
    print "  args",args
    print "  field",field
    print "  value",value
    print "this %s should equal this %s" %  ( reduce(lambda d, k: d[k], self.current_path + [field], self.document), value )

  def _validate_schema(self, schema, field, value):
      self.current_path.append(field)
      super(Validator,self)._validate_schema( schema, field, value )
      self.current_path.pop()


def validate( data, schema ):

  v = Validator( schema )
  if not v.validate(data):
    raise cerberus.ValidationError(yaml.dump(v.errors, default_flow_style=False))

