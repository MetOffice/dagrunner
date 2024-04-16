# Module: `dagrunner.runner.schedulers.dask`

[Source](../dagrunner/runner/schedulers/dask.py#L0)

Standardised UI for dask compatible schedulers (including 'dask on ray')

All have in common that they convert the provided workflow dictionary into a
dask graph by initiating a dask Delayed container on each node and then
executing it (by calling its compute method) using the specified scheduler.
See the following useful background reading:

    - https://docs.dask.org/en/latest/scheduler-overview.html
    - https://docs.dask.org/en/latest/scheduling.html
    - https://docs.dask.org/en/latest/delayed.html

# Class: `DaskOnRay`

[Source](../dagrunner/runner/schedulers/dask.py#L156)

### Call Signature:

```python
DaskOnRay(num_workers, profiler_filepath=None, **kwargs)
```

# Class: `Distributed`

[Source](../dagrunner/runner/schedulers/dask.py#L76)

### Call Signature:

```python
Distributed(num_workers, profiler_filepath=None, **kwargs)
```

# Class: `SingleMachine`

[Source](../dagrunner/runner/schedulers/dask.py#L107)

### Call Signature:

```python
SingleMachine(num_workers, scheduler='processes', profiler_filepath=None, **kwargs)
```

# Function: `add_dummy_tasks`

[Source](../dagrunner/runner/schedulers/dask.py#L30)

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

# Function: `no_op`

[Source](../dagrunner/runner/schedulers/dask.py#L25)

### Call Signature:

```python
no_op(*args, **kwargs)
```

Dummy operation for our dask graph See [add_dummy_tasks](#add_dummy_tasks)

