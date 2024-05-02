# module: `dagrunner.execute_graph`

[Source](../dagrunner/execute_graph.py#L0)

see [module: dagrunner.utils.logger](dagrunner.utils.logger.md#module-dagrunnerutilslogger)

# class: `ExecuteGraph`

[Source](../dagrunner/execute_graph.py#L159)

### Call Signature:

```python
ExecuteGraph(networkx_graph: str, plugin_executor: <built-in function callable> = <function plugin_executor at 0x7f60939fad40>, scheduler: str = 'processes', num_workers: int = 1, profiler_filepath: str = None, dry_run: bool = False, verbose: bool = False, sqlite_filepath: str = None, **kwargs)
```

see [class: dagrunner.plugin_framework.NodeAwarePlugin](dagrunner.plugin_framework.md#class-nodeawareplugin)

see [class: dagrunner.utils.ObjectAsStr](dagrunner.utils.md#class-objectasstr)

# dict: `SCHEDULERS`

# class: `SkipBranch`

[Source](../dagrunner/execute_graph.py#L33)

This exception is used to skip a branch of the execution graph.

To be used in combination to one of the multiprocessing schedulers.
In the single-threaded scheduler, Dask executes tasks sequentially, and
exceptions will propagate as they occur, potentially halting the execution of
subsequent tasks.

see [class: dagrunner.utils.TimeIt](dagrunner.utils.md#class-timeit)

see [function: dagrunner.utils.function_to_argparse](dagrunner.utils.md#function-function_to_argparse)

# function: `main`

[Source](../dagrunner/execute_graph.py#L257)

### Call Signature:

```python
main()
```

Entry point of the program.
Parses command line arguments and executes the graph using the ExecuteGraph class.

# function: `plugin_executor`

[Source](../dagrunner/execute_graph.py#L46)

### Call Signature:

```python
plugin_executor(*args, call=None, verbose=False, dry_run=False, common_kwargs=None, **node_properties)
```

Executes a plugin function or method with the provided arguments and keyword arguments.

Args:
- `*args`: Positional arguments to be passed to the plugin function or method.
- `call`: A tuple containing the callable object or python dot path to one, and its keyword arguments.
- `verbose`: A boolean indicating whether to print verbose output.
- `dry_run`: A boolean indicating whether to perform a dry run without executing the plugin.
- `common_kwargs`: A dictionary of optional keyword arguments to apply to all applicable plugins.
    That is, being passed to the plugin call if such keywords are expected from the plugin.
    This is a useful alternative to global or environment variable usage.
- `**node_properties`: Node properties.  These will be passed to 'node-aware' plugins.

Returns:
- The result of executing the plugin function or method.

Raises:
- ValueError: If the `call` argument is not provided.

see [function: dagrunner.utils.visualisation.visualise_graph](dagrunner.utils.visualisation.md#function-visualise_graph)

