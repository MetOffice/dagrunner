# module: `dagrunner.execute_graph`

[Source](../dagrunner/execute_graph.py#L0)

see [class: dagrunner.utils.CaptureProcMemory](dagrunner.utils.md#class-captureprocmemory)

see [class: dagrunner.plugin_framework.NodeAwarePlugin](dagrunner.plugin_framework.md#class-nodeawareplugin)

see [class: dagrunner.utils.TimeIt](dagrunner.utils.md#class-timeit)

see [function: dagrunner.utils.function_to_argparse_parse_args](dagrunner.utils.md#function-function_to_argparse_parse_args)

see [module: dagrunner.utils.logger](dagrunner.utils.logger.md#module-dagrunnerutilslogger)

see [function: dagrunner.utils.visualisation.visualise_graph](dagrunner.utils.visualisation.md#function-visualise_graph)

## class: `ExecuteGraph`

[Source](../dagrunner/execute_graph.py#L266)

### Call Signature:

```python
ExecuteGraph(networkx_graph: str, networkx_graph_kwargs: dict = None, <function plugin_executor>, scheduler: str = 'processes', num_workers: int = 1, profiler_filepath: str = None, dry_run: bool = False, verbose: bool = False, **kwargs)
```

### function: `__call__`

[Source](../dagrunner/execute_graph.py#L363)

#### Call Signature:

```python
__call__(self)
```

Call self as a function.

### function: `__init__`

[Source](../dagrunner/execute_graph.py#L267)

#### Call Signature:

```python
__init__(self, networkx_graph: str, networkx_graph_kwargs: dict = None, <function plugin_executor>, scheduler: str = 'processes', num_workers: int = 1, profiler_filepath: str = None, dry_run: bool = False, verbose: bool = False, **kwargs)
```

Execute a networkx graph using a chosen scheduler.

Args:
- `networkx_graph` (networkx.DiGraph, callable or str):
  A networkx graph; dot path to a networkx graph or callable that returns
  one; tuple representing (edges, nodes) or callable object that
  returns a networkx.
- `networkx_graph_kwargs` (dict):
  Keyword arguments to pass to the networkx graph callable.  Optional.
- `plugin_executor` (callable):
  A callable object that executes a plugin function or method with the provided
  arguments and keyword arguments.  By default, uses the `plugin_executor`
  function.  Optional.
- `scheduler` (str):
  Accepted values include "ray", "multiprocessing" and those recognised
  by dask: "threads", "processes" and "single-threaded" (useful for debugging).
  See https://docs.dask.org/en/latest/scheduling.html.  Optional.
- `num_workers` (int):
  Number of processes or threads to use.  Optional.
- `dry_run` (bool):
  Print executed commands but don't actually run them.  Optional.
- `profiler_filepath` (str):
  Output html profile filepath if supported by the chosen scheduler.
  See https://docs.dask.org/en/latest/diagnostics-local.html
  Optional.
- `verbose` (bool):
  Print executed commands.  Optional.
- `**kwargs`:
  Optional global keyword arguments to apply to all applicable plugins.

### function: `visualise`

[Source](../dagrunner/execute_graph.py#L360)

#### Call Signature:

```python
visualise(self, output_filepath: str)
```

## dict: `SCHEDULERS`

## _SKIP_EVENT: `SKIP_EVENT`

## class: `SkipBranch`

[Source](../dagrunner/execute_graph.py#L53)

This exception is used to skip a branch of the execution graph.

To be used in combination to one of the multiprocessing dask schedulers.
In the single-threaded scheduler, Dask executes tasks sequentially, and
exceptions will propagate as they occur, potentially halting the execution of
subsequent tasks.

## Warning

Status: experimental.

## function: `main`

[Source](../dagrunner/execute_graph.py#L374)

### Call Signature:

```python
main()
```

Entry point of the program.
Parses command line arguments and executes the graph using the ExecuteGraph class.

## function: `plugin_executor`

[Source](../dagrunner/execute_graph.py#L85)

### Call Signature:

```python
plugin_executor(*args, call=None, verbose=False, dry_run=False, common_kwargs=None, **node_properties)
```

Executes a plugin callable with the provided arguments and keyword arguments.

Plugins can be functions or classes.  If a class, it is instantiated with the
keyword arguments provided in the `call` tuple.  The plugin callable is then
executed with the positional arguments provided in `args` and the keyword arguments
provided in the `call` tuple.  A plugin call is skipped if 1 or more of the `args`
is the `SKIP_EVENT` object.

Args:
- `*args`: Positional arguments to be passed to the plugin callable.
- `call`: A tuple containing the callable object or python dot path to one, keyword
  arguments to instantiate this class (optional and where this callable is a class)
  and finally the keyword arguments to be passed to this callable.
- `verbose`: A boolean indicating whether to print verbose output.
- `dry_run`: A boolean indicating whether to perform a dry run without executing
  the plugin.
- `common_kwargs`: A dictionary of optional keyword arguments to apply to all
  applicable plugins.  That is, being passed to the plugin initialisation and or
  call if such keywords are expected from the plugin.  This is a useful alternative
  to global or environment variable usage.
- `**node_properties`: Node properties.  These will be passed to 'node-aware'
  plugins.

Returns:
- The result of executing the plugin function or method.

Raises:
- ValueError: If the `call` argument is not provided.

