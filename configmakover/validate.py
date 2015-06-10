
import cerberus
import dpath.util

from .render import *


def validate( data, schema ):
  v = cerberus.Validator( schema )
  if not v.validate(data):
    raise cerberus.ValidationError(yaml.dump(v.errors, default_flow_style=False))

