Mako-powered Configuration Files
================================

Configure your application with the power of Mako templates.

Example
-------
YAML is a great language for writing configuration files. It is simple to write, configuration options
can be stored in a logical hierarchy, and it is easy to get into your Python code. config-makover simply
adds the power of Mako Expressions to you YAML file so you can do something like:

    #! /usr/bin/python

    from configmakover.read import *

    text = '''
    <%!
      import math
    %>
    var1 : 1
    var2 : some string
    var3 : 3
    var4 : ${var3 + math.pi + 2}
    var5 : ${var4 + 2.0}
    nest1 :
      var1 : 11
      var2 : ${var3 + 12}
      var3 : ${var1 + 12}
      var4 : ${var3 + 12}
      var5 : ${nest1['var3'] + 12}
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
configuration parameter, or 2) give you configuration file a makeover with config-makover (I know, it's ridiculous),

    # heat solver configuration
    grid:
      x:
        min : 0
        max : 10
        N   : ${int( (max - min)/0.1 )}
      y:
        min : 0
        max : 20
        N   : ${int( (max - min)/0.1 )}
    time:
      start : 0
      stop : 10
      dt : 0.001

If you chose to modify your code to a accept a resolution parameter, you would have to write logic to check which parameter was specified, N or dx. But what
if both where given? By using config-makover, you keep your configuration logic simple while having power to create configurations that auto-compute
parameter values. What if you want the x and y resolution to be the same, but you would like to be able to easily change it?

    # heat solver configuration
    <%!
      res = 0.001
    %>
    grid:
      x:
        min : 0
        max : 10
        N   : ${int( (max - min)/res )}
      y:
        min : 0
        max : 20
        N   : ${int( (max - min)/res )}
    time:
      start : 0
      stop : 10
      dt : 0.001

Because Mako expressions are just Python expressions, you can pretty much do anything you want! It's time to give you configuration a makeover, write
it once, configure forever (ugh, how cheesy can we get?)

Installation
------------
Just copy the configmakover directory to a directory in your PYTHONPATH
(It's still early, I have not put very much polish on it yet).  However,
configmakover currently uses a patched version of Mako that allows for
missing parameters to be ignored (actually, it allows any expression that
contains an error to be ignored). Currently this patched version is available at
https://bitbucket.org/CD3/mako.
