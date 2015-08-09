Template Configuration Files
================================

Configure your application with the power of templates.

Features
--------

`config-makover` is a module that allows you to write configuration files containing Tempita template expressions.
These can be used to do simple variable substitution (have one parameter in your configuration file be automatically
set to the value of another parameter) or more complicated computations (have the value of a parameter
be automatically calculated from another parameter). It has the following features.

  - Recursive parameter substitution. Configuration data is stored in a tree an parameter substitution occurs
    within branches of the tree.
  - Parameter calculation. Configuration data can be automatically calculated using Python expressions.
  - It is file format agnostic. `config-makover` does not parse configuration files. It relies on a "loader".
    If you have a function that can take a string contining the text of your configuration file and return
    a configuration tree (nested dict and list) then you can use config-makeover.
  - Filters. You can provide a list of callables that will be applied to every element in the configuration
    tree before, during, or after the rendering process. Need to make sure all parameters that can be cast
    to a number are numbers? Just write a filter (actually, this is done by default). Want to have any values
    containing a list of numbers ( '1,2,3,4' ) to expand into an actual list? Just write a filter.

###What's with the name?
`config-makover` originally used Mako as its template engine, but it required a modified version to allow multiple
passes on a single template (Mako will fail if an undefined variable is references in an expression). The Mako
project was not interested in adding support for passing through expressions that failed unmodified (so
that future passes on the same template can attempt to replace the expression), so a patched version was used.
However, the only real reason for using Mako was that it supported arbitrary
Python expressions in its templates, which most template engines do not.

Eventually, we found Tempita, which also allows arbitrary python code in its template expressions. It turned out
that Tempita is quite a bit smaller (i.e. simpler) than Mako, and a simple monkey-patch can add the functionality
we need.

Example
-------
YAML is a great language for writing configuration files. It is simple to write, configuration options
can be stored in a logical hierarchy, and it is easy to get into your Python code. `config-makover` simply
adds the power of Mako Expressions to your YAML file so you can do something like:

    #! /usr/bin/python

    from configmakover.read import *

    text = '''
    {{py:
      import math
    }}
    var1 : 1
    var2 : some string
    var3 : 3
    var4 : {{var3 + math.pi + 2}}
    var5 : {{var4 + 2.0}}
    nest1 :
      var1 : 11
      var2 : {{var3 + 12}}
      var3 : {{var1 + 12}}
      var4 : {{var3 + 12}}
      var5 : {{nest1['var3'] + 12}}
    '''


    config = readConfig( text )
    print yaml.dump(config, default_flow_style=False)

The YAML configuration file is loaded into a nested dictionary and then ran through a Mako Template with itself as a Context. The result
is that you can reference the value of other parameters in the configuration file to set the value of a parameter.

This is extremely useful if you write code that does numerical calculations, like a physics simulation.
Consider the following configuration for a physics simulation that solves the 2D heat equation using a Finite-Difference method. You might have a
configuration file that looks like this.

    # heat solver configuration
    grid:
      x:
        min : 0
        max : 10
        N   : 100
      y:
        min : 0
        max : 20
        N   : 200
    time:
      start : 0
      stop : 10
      dt : 0.001

Now suppose you want to be able to set the grid size (N) based on a desired resolution. You could either 1) modify your code to accept a dx and dy
configuration parameter, or 2) give you configuration file a makeover with `config-makover` (I know, it's ridiculous),

    # heat solver configuration
    grid:
      x:
        min : 0
        max : 10
        N   : {{int( (max - min)/0.1 )}}
      y:
        min : 0
        max : 20
        N   : {{int( (max - min)/0.1 )}}
    time:
      start : 0
      stop : 10
      dt : 0.001

If you chose to modify your code to a accept a resolution parameter, you would have to write logic to check which parameter was specified, N or dx. But what
if both where given? By using `config-makover`, you keep your configuration logic simple while having power to create configurations that auto-compute
parameter values. What if you want the x and y resolution to be the same, but you would like to be able to easily change it?

    # heat solver configuration
    {{py:
      res = 0.001
    }}
    grid:
      x:
        min : 0
        max : 10
        N   : {{int( (max - min)/res )}}
      y:
        min : 0
        max : 20
        N   : {{int( (max - min)/res )}}
    time:
      start : 0
      stop : 10
      dt : 0.001

Don't like YAML? No problem, just provide with a parser that reads your preferred format from a string and returns a data tree. So, to read JSON,

    from configmakover.read import *
    import json

    with open('myConfig.json', 'r') as f:
      text = f.read()

    config = readConfig( text, parser=json.loads )

Don't want to learn YAML or JSON? Just use INI,

    from configmakover.read import *
    from configmakover.parsers import ini
    import json

    with open('myConfig.ini', 'r') as f:
      text = f.read()

    config = readConfig( text, parser=ini.load )


Because Mako expressions are just Python expressions, you can pretty much do anything you want! It's time to give you configuration a makeover, write
it once, configure forever (ugh, how cheesy can we get?)

What it does
------------

The ``readConfig`` function reads a configuration string and returns a configuration tree. It does several things in between.

1. The configuration string is passed through Mako as a template. So, you configuration file can be a full blown Mako template as long as this template renders to a string than can be parsed by the loader/de-serializer.

2. The configuration string is parsed by a loader/de-serializer such as YAML.load or JSON.loads.

3. A set of filter functions are called on every element in the configuration tree.

4. The configuration tree is rendered (See details below).

5. A set of filter functions are called on every element in the rendered configuration tree.

6. The data tree is returned.

The rendering step is where most of the work (and power) happens. The rendering
process will replace any references to other parameters in the configuration
tree with their values. This is similar to the parameter interpolation in
ConfigParser, but it is much more powerful. First, the configuration data is
stored in a tree. Second, Mako is used to do the rendering, so all variable
substitution are actually Mako expressions, which means they can contain arbitrary
Python code.

The rendering process consists of several step. The rendering function is called recursively on the branches
of the configuration tree so that it essentially 'walks' down the tree and begins rendering the bottom branches.
This is useful because it allows for 'local' variable substitution. Parameter references will be replaced
with values from the same branch if possible. If the parameter name that is referenced does not exist in
the same branch, then a parameter in the parent branch will be used if it exists. If no parameter exists,
the next highest branch is used, and so on until the top of the tree is reached.

When a specific branch of the configuration tree is being rendered, the following things happen:

1. The "configuration tree" is serialized into a "configuration string". This is done using pickle.

2. A hash of the configuration string is stored.

3. The configuration string is treated as a Mako template and is rendered using the configuration tree
   for the context.

4. The configuration tree is replaced with the tree created from de-serializing the rendered configuration string.

5. A hash of the rendered configuration string is computed and stored.

6. If the new hash matches any other hashes that have been stored, the render function is terminated. Otherwise,
   the process is repeated with the updated configuration tree.

In addition to these steps, a set of user defined functions are used to "filter" the configuration tree elements
after each Mako render.  This allows the caller to process the configuration data in between renderings. For
example, you may need to make sure that all elements that can be converted to numbers are converted to numbers
before the next render occurs so that their values can be used calculations performed by other expressions.

Installation
------------
Just copy the configmakover directory to a directory in your PYTHONPATH
(It's still early, I have developed an installer).  However,
configmakover currently uses a patched version of Mako that allows for
missing parameters to be ignored (actually, it allows any expression that
contains an error to be ignored). Currently this patched version is available at
https://bitbucket.org/CD3/mako.

The makover.py script
---------------------

If you don't have a Python interface to your application, you can still use `config-makover`. A script named
``makover.py`` is included that can read a templated configuration file and write a rendered configuration file.
