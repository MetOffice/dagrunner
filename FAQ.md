# FAQ

## Why NetworkX?
[NetworkX](https://networkx.org/en/) is as close to a standard in python graph representation as there is.

## Why not Prefect/Dagster/Apache Airflow/Luigi, etc.?
DAGrunner is neither a scheduler nor an orchestration engine. Instead, it provides an abstraction layer that decouples the execution graph from the technology used to execute it. Prefect, Dagster, Airflow and Luigi solve a different problem: they are orchestration frameworks, whereas DAGrunner is intended to remain independent of any particular orchestration or scheduling solution.

## What do I need to execute my graph with DAGrunner?

- A Python environment containing NetworkX and a supported scheduler (see [schedulers](README.md#schedulers)).
- A graph consisting of nodes, their associated attributes (collectively referred to as settings), and edges defining the connectivity between them.

The example below defines a simple graph that starts with a node returning 0, passes the result to a node that adds 2, and then to a final node that adds 5, producing a final result of 7:

```python
def add(*arg, const=0):
    return sum(arg) + const

node0 = 'a'
node1 = 'b'
node2 = 'c'

settings = {
    node0: {'call': (lambda : 0,)}
    node1: {'call': (add, const=2)}
    node2: {'call': (add, const=5)}
}
edges = [
    [node0, node1],
    [node1, node2],
]

graph = ExecuteGraph((edges, settings))
graph()
```

While this example is intentionally simple, node execution logic can be arbitrarily complex. See [Example DAGrunner usage](README.md#example-dagrunner-usage) for more advanced examples.

## If multiple outputs share the same inputs or intermediate calculations, will DAGrunner only execute them once?

Yes, provided they are represented by the same node in the graph. DAGrunner executes the graph exactly as supplied and has no awareness of what individual nodes do. If two outputs (for example, `E` and `F`) depend on the same input nodes (`A`, `B`) and the same intermediate node (`C`), those nodes will only be executed once and their results reused by downstream nodes.

If `A`, `B` or `C` appear as separate nodes with different identities, DAGrunner will treat them as independent tasks and execute each one separately. Any reuse therefore comes from how the graph is constructed, not from DAGrunner identifying equivalent computations at runtime.

## Will Cylc be added as a scheduler?

DAGrunner isn't a scheduler and cylc is more an orchestration engine.  Cylc workflows can indeed call DAGrunner to execute a graph with your chosen python scheduler easy enough by utilising the [DAGrunner commandline script](README.md#execution-of-a-networkx-graph-using-dagrunner-execute-graph-script).

## Is the order of predecessors to a node preserved?

This is more a question of NetworkX), rather than DAGrunner.
However, NetworkX graphs [respect insertion order](https://networkx.org/documentation/stable/reference/classes/index.html#basic-graph-types) as its classes are internally implemented using Python dictionaries which since Python 3.7, dictionaries officially preserve insertion order as part of the language specification.  Since DAGrunner uses NetworkX and dictionaries itself internal, order is similarly preserved.
