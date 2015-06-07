#! /usr/bin/env python

import sys, os
moddir = os.path.join( os.path.dirname( __file__ ), '..' )
sys.path = [moddir] + sys.path

from configmakover.read import *
import json
import yaml

from argparse import ArgumentParser

parser = ArgumentParser(description="Makover a set config files.")

parser.add_argument("infile",
                    action="store",
                    help="Config files to makover." )

parser.add_argument("-f", "--format",
                    action="store",
                    default="yaml",
                    help="File format." )

parser.add_argument("-o", "--output",
                    action="store",
                    default="-",
                    help="Output file",)


args = parser.parse_args()

outfile = args.output



with open(args.infile, 'r') as f:
  text = f.read()

loader = yaml.load
dumper = yaml.dump

if args.format.lower() == 'json':
  loader = yaml.loads
  dumper = yaml.dumps


config = readConfig( text, parser=loader )

text = dumper( config )

if outfile == '-':
  print text
else:
  with open(outfile, 'w') as f:
    f.write(text)


