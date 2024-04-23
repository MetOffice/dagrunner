[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Experimental](https://img.shields.io/badge/status-experimental-orange)
![Python Project](https://img.shields.io/badge/language-Python-blue?logo=python&logoColor=white)
![Static Badge](https://img.shields.io/badge/pip%20install-blue)

# Dagrunner

Dagrunner serves as a Directed Acyclic Graph (DAG) runner, primarily designed to ensure a clear distinction between a project's graph definition (typically in native networkx format) and its execution method. In essence, Dagrunner offers various schedulers for executing the graph, but it firmly separates these operational concepts from the scientific configuration or recipe, i.e., the graph itself. Consequently, while Dagrunner currently provides convenient scheduling options, it remains adaptable to future changes or alternative solutions, ensuring that the scientific configuration can persist regardless of the technologies or tools employed, whether Dagrunner is utilized or not.

## License/copyright

(C) Crown Copyright, Met Office. All rights reserved.

This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
See LICENSE in the root of the repository for full licensing details.

## Installation

The package is [pip](https://pip.pypa.io/en/stable/) installable.  Note that dependencies are expected to be installed via conda (at this time).
```
pip install .
```

(uninstall: `pip uninstall dagrunner`)

This will also make an executable script available to the PATH: `dagrunner-execute-graph`

## Execution of a networkx graph using `dagrunner-execute-graph` script

```
usage: dagrunner-execute-graph [-h] [--scheduler SCHEDULER] [--num-workers NUM_WORKERS] [--profiler-filepath PROFILER_FILEPATH] [--dry-run] [--verbose] networkx-graph
```
see `dagrunner-execute-graph --help` for more information.

## Example library usage

Let's demonstrate defining a graph, where in our simple example we define each node with an associated ID.  Our task is then to concatenate this node ID as a string with its dependencies.

This demonstrates:
- Defining a custom processing module (i.e. plugin).
- Basic graph generation.
- Passing data in memory.
- Execution with our chosen scheduler.

### Defining a custom processing module (plugin)

First, ensure that 'dagrunner' is on the `PYTHONPATH` (i.e. [installation](#installation)).

Now let's subclass the abstract 'Plugin' class from `dagrunner` and define a processing module that accepts an 'id' as argument and concatenates this together with the node ID (result returned) of dependent (predecessor) nodes.

```python
from dagrunner.plugin_framework import Plugin

class ProcessID(Plugin):
    """Concatenate node id together"""
    def __call__(self, *args, id=None, verbose=False):
        concat_arg_id = str(id)
        if args and args[0]:
            concat_arg_id = '_'.join([str(arg) for arg in args if arg]) + f"_{id}"
        return concat_arg_id
```

### Define our graph 'nodes' container

Our node could represent any range of properties but for the purpose of this example we will define only 'step' and 'leadtime' properties.
Also we could define any object to represent a 'node' but commonly used objects for this purpose include [dataclasses](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) and [namedtuples](https://docs.python.org/3/library/collections.html#collections.namedtuple).
For the sake of graph visualisation, we will define a `__str__` special method too.

```python
from dataclasses import dataclass

@dataclass(order=True, eq=True, frozen=True)
class Node:
    step: str = None
    leadtime: int = None

    def __str__(self):
        return f"S:{self.step}_L:{self.leadtime}"
```

### Define the graph itself (configuration/recipe depending on preferred terminology)

Let's define a graph with two independent branches.  One for the earlier leadtime and a second for the later leadtime.
```python
HOUR = 3600
MINUTE = 60
leadtimes = tuple(range(0, HOUR*2, HOUR))

SETTINGS = {}
EDGES = []

for leadtime in leadtimes:
    # node1 -> node2
    node1 = Node(step="step1", leadtime=leadtime)
    node2 = Node(step="step2", leadtime=leadtime)
    EDGES.append([node1, node2])

    # node3 -> node4
    node3 = Node(step="step3", leadtime=leadtime)
    node4 = Node(step="step4", leadtime=leadtime)
    EDGES.append([node3, node4])

    # node2 -> node5
    node5 = Node(step="step5", leadtime=leadtime)
    EDGES.append([node2, node5])

    # node4 -> node5
    node4 = Node(step="step4", leadtime=leadtime)
    EDGES.append([node4, node5])

    for nodenum in range(1, 6):
        node = vars()[f"node{nodenum}"]
        SETTINGS[node] = {
            'call': tuple([ProcessID, {"id": nodenum}]),
        }
```
We see that the processing step callable is provided via the 'call' of the node attribute dictionary.
It's value is `(callable, callable_keyword_arguments)`.
This 'callable' can be a python module dot path, callable function or even a class.

### Execute our graph with our chosen scheduler

For the execution of our graph, we will make use of the built-in generic `ExecuteGraph` class.
This class accepts graphs taking the form of a python dot module path to a networkx, a `networkx.DiGraph` object or a tuple containing `(edges, nodes)`.  In our simple example here, we will pass our edges and nodes above so that `ExecuteGraph` can construct our networkx graph for us.

Here we provide our edges and settings (nodes) and choose the 'single-threaded' scheduler.

```python
from dagrunner.execute_graph import ExecuteGraph
graph = ExecuteGraph((EDGES, SETTINGS), num_workers=None, scheduler="single-threaded", verbose=True)
```

Let's visualise our Networkx first:
```python
import networkx as nx
nx.draw(graph.nxgraph, with_labels=True)
```
![image](https://github.com/MetOffice/dagrunner/assets/2071643/de103edd-16c9-487a-bf22-3d50d81c908c)

Now, finally, let's execute it:
```python
graph()
```
```
args: []
call: (<class '__main__.ProcessID'>, {'id': 1})
ProcessID(*[], **{'id': 1})
result: '1'
args: ['1']
call: (<class '__main__.ProcessID'>, {'id': 2})
ProcessID(*['1'], **{'id': 2})
result: '1_2'
args: []
call: (<class '__main__.ProcessID'>, {'id': 3})
ProcessID(*[], **{'id': 3})
result: '3'
args: ['3']
call: (<class '__main__.ProcessID'>, {'id': 4})
ProcessID(*['3'], **{'id': 4})
result: '3_4'
args: ['1_2', '3_4']
call: (<class '__main__.ProcessID'>, {'id': 5})
ProcessID(*['1_2', '3_4'], **{'id': 5})
result: '1_2_3_4_5'
args: []
call: (<class '__main__.ProcessID'>, {'id': 1})
ProcessID(*[], **{'id': 1})
result: '1'
args: ['1']
call: (<class '__main__.ProcessID'>, {'id': 2})
ProcessID(*['1'], **{'id': 2})
result: '1_2'
args: []
call: (<class '__main__.ProcessID'>, {'id': 3})
ProcessID(*[], **{'id': 3})
result: '3'
args: ['3']
call: (<class '__main__.ProcessID'>, {'id': 4})
ProcessID(*['3'], **{'id': 4})
result: '3_4'
args: ['1_2', '3_4']
call: (<class '__main__.ProcessID'>, {'id': 5})
ProcessID(*['1_2', '3_4'], **{'id': 5})
result: '1_2_3_4_5'
Run-time: 20.03338298993185s
```
We can see that the 'result' of the two execution branches (each leadtime), demonstrates the concatenation of node IDs.
That is, the concatenation of node ID strings passed between nodes in the execution graph.

## Customising graph generation and its execution

### Customise graph construction

Graph construction is owned by the you, the user (project) that utilises **dagrunner**.
We saw how to execute our graph in our [example](#execute-our-graph-with-our-chosen-scheduler).  This `ExecuteGraph` class provides a means to customise what graph we actually execute by providing the means to pass it a **callable** which returns a networkx graph.
As mentioned previously, this can be a python dot module path or the object itself.

Typical uses include delaying the construction of your networkx graph until it is actually executed.  However, this offset complete flexibility for you to customise graph construction to your individual projects needs.

Note that modifying graph construction is an added complication and should not be considered only where it is deemed absolutely necessary beyond the simple usecase (lazy construction).

#### example lazy graph construction

Let's say we define our edges and settings in the above [example](#example-library-usage) in a module accessed by 'node-edge-module-dot-path', a python module dot path.  In this case, containing `EDGES` and `SETTINGS` objects.
We can then define a callable which is responsible for generating a networkx graph for these (when called).

```python
from importlib import import_module
import networkx as nx

def filter_missing(node):
    return {k: v for k, v in vars(node).items() if v is not None}

def gen_networkx(config_dot_path):
    edges = []
    nodes = []
    config_subpkg = import_module(f"{config_dot_path}")
    for module in config_subpkg.__all__:
        print(f"config_dot_path: {config_dot_path}, module: {module}")
        mod = import_module(f"{config_dot_path}.{module}")
        edges.extend(mod.EDGES)
        nodes.extend({k: mod.SETTINGS[k] | filter_missing(k) for k in mod.SETTINGS.keys()}.items())
    graph = nx.DiGraph()
    graph.add_edges_from(edges)
    graph.add_nodes_from(nodes)
    return graph

GRAPH = lambda: gen_networkx("<node-edge-module-dot-path>")
```
We can now provide a python module dot path to this graph object to the `dagrunner-execute-graph` script.  The networkx graph will then be constructed when dagrunner internally calls it before its execution.

### Customise node execution

The `ExecuteGraph` class provides a means to provides a means to provide a custom 'plugin_executor' (rather than to use the built-in).

The 'plugin_executor' is what wraps every 'node' and is responsible for understanding how to 'execute' the particular node it wraps.  For example, the built-in plugin-executor defines the contract we utilise in our example graph above, where 'call' takes the form `(callable object or python dot path to callable, callable keyword arguments)`.  For each node, this plugin executor then calls the underlying processing module (plugin) with its provided arguments (as per 'call').

#### an example extended 'plugin-executor'

```python
from dagrunner.execute_graph import ExecuteGraph, plugin_executor

def custom_plugin_executor(*args, call=None, verbose=False, dry_run=False, **kwargs):
    # do something custom
    return plugin_executor(*args, call=call, verbose=verbose, dry_run=dry_run, **kwargs)
```

Now, let's execute our graph with our customised execution function.
```python
ExecuteGraph(..., plugin_executor=custom_plugin_executor, ...)
```
Note that you may choose to subclass `ExecuteGraph` and or write a custom commandline script to call it, depending on your requirements.

## Processing modules (aka plugins)

Dagrunner concerns itself with graph execution and does not strictly require processing modules (plugins) to take any particular form.  That is, you may or may not choose to use or subclass the plugins provided by dagrunner.
However, for convenience, dagrunner does define some plugins which fall into two broad categories, as defined by two abstract classes.  One is the basic 'Plugin' which defines a reasonable standard UI.  The other is 'NodeAwarePlugin'.  This is identical to the basic 'Plugin' but additionally triggers the the built-in plugin-executor function to pass your plugin all of its node parameters (i.e. extend the keyword arguments with node properties in its call).  That is, making the plugin we define 'node aware'.

Plugins included:
- `Plugin`: Abstract class on which to define other plugins.
- `NodeAwarePlugin`: Abstract class on which to define 'node aware' plugins.
- `Shell(Plugin)`: Execute a subprocess command.
- `DataPolling(Plugin)`: Poll for availability of files.
- `Input(NodeAwarePlugin)`: Given a filepath, expand it using keyword argument, environment variables and any node properties provided.

## Schedulers

The `dagrunner-execute-graph` script exposes a scheduler argument for specifying our preferred scheduler.  Schedulers include [dask](https://www.dask.org/), [ray](https://docs.ray.io/en/latest/ray-more-libs/dask-on-ray.html) and multiprocessing async scheduler (in-house scheduler utilising python built-in [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) library).  See command help for further details.
