# Module: `dagrunner.runner.schedulers.asyncmp`

[Source](../dagrunner/runner/schedulers/asyncmp.py#L0)

# Class: `AsyncMP`

[Source](../dagrunner/runner/schedulers/asyncmp.py#L12)

### Call Signature:

```python
AsyncMP(nprocesses, *args, fail_fast=True, profiler_filepath=None, **kwargs)
```

Basic asynchronous scheduler using python built-in multiprocessing.

Context manager for creating a pool of workers, submits jobs based on the
condition of their dependencies completing, then finally tidies up after
itself.

