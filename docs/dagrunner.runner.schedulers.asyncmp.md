# module: `dagrunner.runner.schedulers.asyncmp`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/runner/schedulers/asyncmp.py#L0)

## class: `AsyncMP`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/runner/schedulers/asyncmp.py#L12)

### Call Signature:

```python
AsyncMP(nprocesses, *args, fail_fast=True, profiler_filepath=None, **kwargs)
```

Basic asynchronous scheduler using python built-in multiprocessing.

Context manager for creating a pool of workers, submits jobs based on the
condition of their dependencies completing, then finally tidies up after
itself.

### function: `__enter__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/runner/schedulers/asyncmp.py#L137)

#### Call Signature:

```python
__enter__(self)
```

Initiate the pool of workers.

### function: `__exit__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/runner/schedulers/asyncmp.py#L142)

#### Call Signature:

```python
__exit__(self, exc_type, exc_value, exc_traceback)
```

Prevents any more tasks from being submitted to the pool.
Once all the tasks have been completed the worker processes will
exit.

### function: `__init__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/runner/schedulers/asyncmp.py#L22)

#### Call Signature:

```python
__init__(self, nprocesses, *args, fail_fast=True, profiler_filepath=None, **kwargs)
```

Initialise our asynchronous multiprocessing scheduler, ready to be used.

Args:
- nprocesses (int):
  Number of processes to use.
- *args:
  Positional arguments to be passed to the multiprocessing pool call.

Keyword Args:
- fail_fast (bool):
  When a job is found to raise an exception, stop submiting new jobs
  to the queue.  If fail_fast is True, terminate all currently running
  jobs.  If False, wait for already queued jobs to complete.
- **kwargs:
  Keyword arguments to be passed to the multiprocessing pool call.

### function: `run`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/runner/schedulers/asyncmp.py#L51)

#### Call Signature:

```python
run(self, graph, verbose=False, poll_frequency=0.5)
```

Run the provided graph using multiprocessing.

Args:
- graph (dict):
  Dictionary, mapping targets to an iterable of commands.

Keyword Args:
- verbose (bool):
  Print out statements indicating progress.
- poll_frequency (float):
  This is the frequency in seconds which we poll running processes.
  Dependent nodes are run if their predecessors are completed,
  as verified by this polling of status.

