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

Here we provide our edges and settings (nodes) and choose the 'single-threaded' scheduler.

We could have constructed the `networkx.DiGraph` ourselves and passed this instead (in fact that would be preferable).  Alternatively, as with the 'plugins',
we could also have provided a python dot module path to our networkx graph or to a callable that returns it.
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
