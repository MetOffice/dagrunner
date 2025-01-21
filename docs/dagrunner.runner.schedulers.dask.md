# module: `dagrunner.runner.schedulers.dask`

[Source](../dagrunner/runner/schedulers/dask.py#L0)

Standardised UI for dask compatible schedulers (including 'dask on ray')

All have in common that they convert the provided workflow dictionary into a
dask graph by initiating a dask Delayed container on each node and then
executing it (by calling its compute method) using the specified scheduler.
See the following useful background reading:

    - https://docs.dask.org/en/latest/scheduler-overview.html
    - https://docs.dask.org/en/latest/scheduling.html
    - https://docs.dask.org/en/latest/delayed.html

## class: `DaskOnRay`

[Source](../dagrunner/runner/schedulers/dask.py#L217)

### Call Signature:

```python
DaskOnRay(num_workers, profiler_filepath=None, **kwargs)
```

A class to run dask graphs using the 'dak-on-ray' scheduler.

### function: `__enter__`

[Source](../dagrunner/runner/schedulers/dask.py#L225)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../dagrunner/runner/schedulers/dask.py#L228)

#### Call Signature:

```python
__exit__(self, exc_type, exc_value, exc_traceback)
```

### function: `__init__`

[Source](../dagrunner/runner/schedulers/dask.py#L220)

#### Call Signature:

```python
__init__(self, num_workers, profiler_filepath=None, **kwargs)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `run`

[Source](../dagrunner/runner/schedulers/dask.py#L233)

#### Call Signature:

```python
run(self, dask_graph, verbose=False)
```

Execute the provided graph.

Args:
- dask_graph (dict): Dask graph dictionary

Keyword Args:
- verbose (bool): Print out statements indicating progress.

Returns:
- Any: The output of the graph execution.

## class: `Distributed`

[Source](../dagrunner/runner/schedulers/dask.py#L84)

### Call Signature:

```python
Distributed(num_workers, profiler_filepath=None, **kwargs)
```

A class to run dask graphs on a distributed cluster.

### function: `__enter__`

[Source](../dagrunner/runner/schedulers/dask.py#L97)

#### Call Signature:

```python
__enter__(self)
```

Create a local cluster and connect a client to it.

### function: `__exit__`

[Source](../dagrunner/runner/schedulers/dask.py#L111)

#### Call Signature:

```python
__exit__(self, exc_type, exc_value, exc_traceback)
```

### function: `__init__`

[Source](../dagrunner/runner/schedulers/dask.py#L87)

#### Call Signature:

```python
__init__(self, num_workers, profiler_filepath=None, **kwargs)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `run`

[Source](../dagrunner/runner/schedulers/dask.py#L115)

#### Call Signature:

```python
run(self, dask_graph, verbose=False)
```

Execute the provided graph.

Args:
- dask_graph (dict): Dask graph dictionary

Keyword Args:
- verbose (bool): Print out statements indicating progress.

Returns:
- Any: The output of the graph execution.

## class: `SingleMachine`

[Source](../dagrunner/runner/schedulers/dask.py#L140)

### Call Signature:

```python
SingleMachine(num_workers, scheduler='processes', profiler_filepath=None, **kwargs)
```

A class to run dask graphs on a single machine.

### function: `__enter__`

[Source](../dagrunner/runner/schedulers/dask.py#L152)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../dagrunner/runner/schedulers/dask.py#L213)

#### Call Signature:

```python
__exit__(self, exc_type, exc_value, exc_traceback)
```

### function: `__init__`

[Source](../dagrunner/runner/schedulers/dask.py#L143)

#### Call Signature:

```python
__init__(self, num_workers, scheduler='processes', profiler_filepath=None, **kwargs)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `run`

[Source](../dagrunner/runner/schedulers/dask.py#L155)

#### Call Signature:

```python
run(self, dask_graph, verbose=False)
```

Execute the provided graph.

Args:
- dask_graph (dict): Dask graph dictionary

Keyword Args:
- verbose (bool): Print out statements indicating progress.

Returns:
- Any: The output of the graph execution.

## function: `add_dummy_tasks`

[Source](../dagrunner/runner/schedulers/dask.py#L38)

### Call Signature:

```python
add_dummy_tasks(dask_graph)
```

Add a terminating dummy task to the graph as well as to each of our
disconnected branches.

A terminating dummy node is added to our graph to allow us to run the
complete graph in one call as well as discard the return.
Dummy nodes (as denoted by 'waiter' prefix in their name) are also added
to the termination of each independent branch, as a single terminal task
on the graph would gather all data (as its input) on the single worker and
potentially blow past its limits. That is, one dummy task per output
effectively ensures that no data leaves the worker.

Args:
- dask_graph (dict): Dask graph dict

Returns:
- dict: Dask graph

TODO:
- Potentially skip intermediate dummy for tasks with no return value.

## function: `no_op`

[Source](../dagrunner/runner/schedulers/dask.py#L30)

### Call Signature:

```python
no_op(*args, **kwargs)
```

Dummy operation for our dask graph See [add_dummy_tasks](#function-add_dummy_tasks)

