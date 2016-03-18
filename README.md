Template Configuration Files
================================

Configure your application with the power of templates.

Features
--------

`config-makover` is a module that allows you to write configuration files containing Tempita template expressions.
These can be used to do simple variable substitution (have one parameter in your configuration file be automatically
set to the value of another parameter) or more complicated computations (have the value of a parameter
be automatically calculated from another parameter). It has the following features.

  - Recursive parameter substitution. Configuration data is stored in a tree and parameter substitution occurs
    within branches of the tree.
  - Parameter calculation. Configuration data can be automatically calculated using Python expressions.
  - Support for quantities. `config-makover` uses `pint` to allow configuration data to be specified in arbitrary units
    and converted to the units that your application expects.
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
However, the only real reason for using Mako in the first place was that it supported arbitrary
Python expressions in its templates, which most template engines do not.

Eventually, we found Tempita, which also allows arbitrary python code in its template expressions. It turned out
that Tempita is quite a bit smaller (i.e. simpler) than Mako, and a simple monkey-patch can add the functionality
we need.

Example
-------
YAML is a great language for writing configuration files. It is simple to write, configuration options
can be stored in a logical hierarchy, and it is easy to get into your Python code. `config-makover` simply
adds the power of Tempita Expressions to your YAML file so you can do something like:

    #! /usr/bin/python

    from configmakover.read import *

    text = '''
    {{py:
      import math
    }}
    var1 : 1
    var2 : some string
    var3 : 3
    var4 : {{c['var3'] + math.pi + 2}}
    var5 : {{c['var4'] + 2.0}}
    nest1 :
      var1 : 11
      var2 : {{c['var3'] + 12}}
      var3 : {{c['var1'] + 12}}
      var4 : {{c['var3'] + 12}}
      var5 : {{c['/nest1/var3'] + 12}}
    '''


    config = readConfig( text )
    print yaml.dump(config, default_flow_style=False)

The YAML configuration file is loaded into a nested dictionary and then ran through a Tempita Template with itself as a Context. The result
is that you can reference the value of other parameters in the configuration file to set the value of a parameter.
The context is passed to Tempita as a `DataTree` named "`c`". A `DataTree` is a lightweight wrapper class around a nested `dict` that allows elements
to be accessed with a path syntax. Think of a `DataTree` as a view on top of a `dict` that adds a few convienent operations.

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
        N   : {{(c['max'] - c['min'])/0.1 )}}
      y:
        min : 0
        max : 20
        N   : {{(c['max'] - c['min'])/0.1 )}}
    time:
      start : 0
      stop : 10
      dt : 0.001

If you chose to modify your code to a accept a resolution parameter, you would have to write logic to check which parameter was specified, N or dx. But what
if both where given? By using `config-makover`, you keep your configuration logic in your application simple while having power to create configurations that auto-compute
parameter values. What if you want the x and y resolution to be the same, but you would like to be able to easily change it?

    # heat solver configuration
    grid:
      res : 0.001
      x:
        min : 0
        max : 10
        N   : {{(c['max'] - c['min'])/c['../res']}}
      y:
        min : 0
        max : 20
        N   : {{(c['max'] - c['min'])/c['../res']}}
    time:
      start : 0
      stop : 10
      dt : 0.001

This example shows the convienence provided by the `DataTree` wrapper. The
`res` parameter can be accessed by its relative path. We could have also used
the absolute path (`c['/grid/res']`).

Don't like YAML? No problem, just
provide the `readConfig` function with a parser that reads your preferred format from a string and
returns a nested dict. So, to read JSON,

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


Because Tempita expressions are just Python expressions, you can pretty much do anything you want! It's time to give you configuration a makeover, write
it once, configure forever (ugh, how cheesy can we get?)

What it does
------------

The ``readConfig`` function reads a configuration string and returns a configuration tree. It does several things in between.

1. The configuration string is passed through Tempita as a template. So, you configuration file can be a full blown Tempita template as long as this template renders to a string than can be parsed by the loader/de-serializer.

1. The configuration string is parsed by a loader/de-serializer such as YAML.load or JSON.loads that creates a nested `dict`.

1. A the nested `dict` is wrapped with a `DataTree`.

1. A set of filter functions are called on every element in the configuration tree.

1. The configuration tree is rendered (See details below).

1. A set of filter functions are called on every element in the rendered configuration tree.

1. The nested `dict` is returned.

The rendering step is where most of the work (and power) happens. The rendering
process will replace any references to other parameters in the configuration
tree with their values. This is similar to the parameter interpolation in
ConfigParser, but it is much more powerful. First, the configuration data is
stored in a tree. Second, Tempita is used to do the rendering, so all variable
substitution are actually Tempita expressions, which means they can contain arbitrary
Python code.

Several things are done to render the configuration tree. Essentially, each (terminal) element in the tree
is passed through the Tempita `sub` function and replaced with the result. A `DataTree` view
of the configuration tree is passed to the `sub` function as the render context, so all of
the parameters in the configuration tree are avaiable in the Tempita expression.

In order to allow multi-level references (i.e. a parameter is references that
references another parameter), this is repeated until the configuration tree does
not change after a complete render. To protect against circular dependencies, a hash
of the tree after each render is stored. If a hash is repeated, the rendering stops.
repeats a previous state).  A modified version of Tempita's `_eval` function is
used so that if an error occurs during the substitution, the template is
returned unmodified. This allows the `sub` function to be called multiple times
on the same template.

The following steps are taken during one render of the configuration tree:

1. A hash of the configuration tree is stored by first pickling the tree, and then creating a hash of the pickle string.

1. A list of all paths to terminal elements in the tree is generated.

1. The element at each path is passed to the Tempita `sub` function.

1. A hash of the rendered configuration string is computed and stored.

1. If the new hash matches any other hashes that have been stored, the render function is terminated. Otherwise,
   the process is repeated with the updated configuration tree.

In addition to these steps, a set of user defined functions are used to "filter" the configuration tree elements
after each Tempita render.  This allows the caller to process the configuration data in between renderings. For
example, you may need to make sure that all elements that can be converted to numbers are converted to numbers
before the next render occurs so that their values can be used calculations performed by other expressions.

Installation
------------

```
python setup.py install
```

The makover.py script
---------------------

If you don't have a Python interface to your application, you can still use `config-makover`. A script named
``makover.py`` is included that can read a templated configuration file and write a rendered configuration file.
