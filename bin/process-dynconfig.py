#! /usr/bin/env python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from dynconfig.read import *
from argparse import ArgumentParser

parser = ArgumentParser(description="Process a set of dynamic config files.")

parser.add_argument("infile",
                    action="store",
                    help="Config file to process." )

parser.add_argument("-f", "--from",
                    dest="_from",
                    action="store",
                    default=None,
                    help="Input file format." )

parser.add_argument("-t", "--to",
                    dest="_to",
                    action="store",
                    default=None,
                    help="Output file format." )

parser.add_argument("-o", "--output",
                    action="store",
                    default="-",
                    help="Output file",)


def ft(fn):
  '''Return filetype from filename.'''
  if fn.endswith(".dync"):
    fn = fn[:-5]
  if fn.endswith("yaml"):
    return "yaml"
  if fn.endswith("yml"):
    return "yaml"
  if fn.endswith("json"):
    return "json"
  if fn.endswith("ini"):
    return "ini"
  if fn.endswith("txt"):
    return "keyval"


args = parser.parse_args()

outfile = args.output
with open(args.infile, 'r') as f:
  text = f.read()

ifmt = ft(args.infile)
if args._from is not None:
  ifmt = args._from.lower()

ofmt = ft(args.output)
if args._to is not None:
  ofmt = args._to.lower()

print ifmt,'->',ofmt
if ifmt == "yaml":
  loader = yaml.load
elif ifmt == "json":
  loader = json.loads
elif ifmt == "ini":
  loader = ini.load
elif ifmt == "keyval":
  loader = keyval.load
else:
  # default
  loader = yaml.load

if ofmt == "yaml":
  dumper = yaml.dump
elif ofmt == "json":
  dumper = json.dumps
elif ofmt == "ini":
  dumper = ini.dump
elif ofmt == "keyval":
  dumper = keyval.dump
else:
  # default
  dumper = yaml.dump


config = readConfig( text, parser=loader )

text = dumper( config )

if outfile == '-':
  print text
else:
  with open(outfile, 'w') as f:
    f.write(text)


