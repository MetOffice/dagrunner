# Module: `dagrunner.execute_graph`

[Source](../dagrunner/execute_graph.py#L0)

# Class: `ExecuteGraph`

[Source](../dagrunner/execute_graph.py#L149)

### Call Signature:

```python
ExecuteGraph(networkx_graph: str, plugin_executor: <built-in function callable> = <function plugin_executor at 0x7ff0e42c2b00>, scheduler: str = 'processes', num_workers: int = 1, profiler_filepath: str = None, dry_run: bool = False, verbose: bool = False, **kwargs)
```

see [NodeAwarePlugin](dagrunner.plugin_framework.md#NodeAwarePlugin)

see [ObjectAsStr](dagrunner.utils.md#ObjectAsStr)

# Object: `SCHEDULERS`

# Class: `SkipBranch`

[Source](../dagrunner/execute_graph.py#L30)

This exception is used to skip a branch of the execution graph.

To be used in combination to one of the multiprocessing schedulers.
In the single-threaded scheduler, Dask executes tasks sequentially, and
exceptions will propagate as they occur, potentially halting the execution of
subsequent tasks.

see [TimeIt](dagrunner.utils.md#TimeIt)

see [function_to_argparse](dagrunner.utils.md#function_to_argparse)

# Function: `main`

[Source](../dagrunner/execute_graph.py#L240)

### Call Signature:

```python
main()
```

Entry point of the program.
Parses command line arguments and executes the graph using the ExecuteGraph class.

# Function: `plugin_executor`

[Source](../dagrunner/execute_graph.py#L43)

### Call Signature:

```python
plugin_executor(*args, call=None, verbose=False, dry_run=False, **kwargs)
```

Executes a plugin function or method with the provided arguments and keyword arguments.

Args:
    *args: Positional arguments to be passed to the plugin function or method.
    call: A tuple containing the callable object or python dot path to one, and its keyword arguments.
    verbose: A boolean indicating whether to print verbose output.
    dry_run: A boolean indicating whether to perform a dry run without executing the plugin.
    **kwargs: Keyword arguments to be passed to the plugin function or method (common to all plugins).

Returns:
    The result of executing the plugin function or method.

Raises:
    ValueError: If the `call` argument is not provided.

see [visualise_graph](dagrunner.utils.visualisation.md#visualise_graph)

