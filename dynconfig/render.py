from .utils import *
import filters as expression_filters
from .pdict import *

import pyparsing

import pickle
import hashlib
import logging
import re

import logging
logging.basicConfig(level=logging.INFO)

import math
default_locals = { 'math' : math, 'm' : math, 'abs' : abs, 'sum' : sum, 'float' : float, 'f' : float, 'int' : int, 'min' : min, 'max' : max }

class parser:
  var_token = pyparsing.Literal('{')  + pyparsing.SkipTo(pyparsing.Literal('}'), failOn=pyparsing.Literal('}')) + pyparsing.Literal('}')
  def replace_var_token( toks ):
    rep = "context['{name}']".format(name=toks[1])
    return rep
  var_token.setParseAction(replace_var_token)
  exp_token = pyparsing.Literal('$(') + pyparsing.SkipTo(pyparsing.Literal(')'), ignore=pyparsing.QuotedString('(',endQuoteChar=')')) + pyparsing.Literal(')')

  filter_name_token = pyparsing.Word(pyparsing.alphanums)
  filter_arg_token  = pyparsing.Word(pyparsing.printables)
  filter_token = filter_name_token("name") + pyparsing.ZeroOrMore( filter_arg_token )("args")



def render( data, repeat = False, locals = {}, filters = {}, strict = False ):
  origdata = data
  data = pdict()
  data.update(origdata)

  local_ns = dict()
  local_ns.update(default_locals)
  local_ns.update(locals)

  exp_filters = dict()
  exp_filters.update( dict([ (re.sub("^filter_","",x),getattr(expression_filters,x)) for x in dir(expression_filters) if x.startswith("filter_") ]) )
  exp_filters.update(filters)

  
  # replace vars
  hashes = dict()
  hash =  hashlib.sha1( pickle.dumps(data) ).hexdigest()
  hashes[hash] = hashes.get(hash,0) + 1
  while hashes.get( hash, 0 ) < 2:
    for k in get_all_pdict_keys(data):
      v = data[k]
      if isinstance(v,(str,unicode)):
        v = parser.var_token.transformString(v)
        data[k] = v
    if not repeat:
      break
    else:
      hash =  hashlib.sha1( pickle.dumps(data) ).hexdigest()
      hashes[hash] = hashes.get(hash,0) + 1

  # replace expressions
  hashes = dict()
  hash =  hashlib.sha1( pickle.dumps(data) ).hexdigest()
  hashes[hash] = hashes.get(hash,0) + 1
  while hashes.get( hash, 0 ) < 2: # repeat until we get the same tree twice
    for k in get_all_pdict_keys(data): # loop through all paths
      if isinstance(data[k],(str,unicode)): # only try to replace values that are strings
        v = data[k]
        newv = v
        offset = 0
        for toks,si,ei in parser.exp_token.scanString(v): # loop through all expressions
          exp_str = toks[1] # the expression string to be evaluated
          logging.info("evaluating expression: '{0}'".format(exp_str))

          exp_str,fchar,filt_str = exp_str.partition('|') # split filters from expression
          context = {'context':data[data.pathname(k)]}    # use element's parent as context
          context.update(local_ns)                        # add local namespace to context
          try:
            try:
              r = eval(exp_str,{'__builtins__':None},context)
            except Exception as e:
              # SPECIAL CASE
              # allow strings to be passed to filters without quotes
              # if filters exists. i.e allow $( 10 us | float ) as a short hand
              # for $( "10 us" | float )
              if filt_str != "":
                r = exp_str
              else:
                raise e
            if filt_str !=  "": # apply filters if they exist
              for fstr in filt_str.split(fchar):
                f = parser.filter_token.parseString(fstr)
                if f.name in exp_filters:
                  rr = exp_filters[f.name](r,*f.args)
                  if rr is not None:
                    r = rr

            logging.info("expression evaluated to: '{0}'".format(r))
            # if the value is just an expression, replace it with whatever eval returned
            if si == 0 and ei == len(v):
              newv = r
            else:
              print newv
              newv = newv[:offset+si]+str(r)+newv[offset+ei:]
              print newv
              print
              offset += len(str(r)) - (ei-si)

          except Exception as e:
            logging.info("expression eval failed with following message: %s"%str(e))
            pass

        data[k] = newv

    if not repeat: # if repeat option is not set, quit now
      break
    else:
      hash =  hashlib.sha1( pickle.dumps(data) ).hexdigest()
      hashes[hash] = hashes.get(hash,0) + 1

  if strict: # check for un-evaluated expressions
    unparsed_exps = []
    for k in get_all_pdict_keys(data):
      if isinstance(data[k],(str,unicode)):
        unparsed_exps += list(parser.exp_token.searchString(data[k]))
    if len(unparsed_exps) > 0:
      raise RuntimeError("Failed to replaced one or more expressions: "+str(unparsed_exps))




  return data



