# module: `dagrunner.execute_graph`

[Source](../dagrunner/execute_graph.py#L0)

see [GlobalConfiguration: dagrunner.config.CONFIG](dagrunner.config.md#globalconfiguration-config)

see [class: dagrunner.utils.CaptureProcMemory](dagrunner.utils.md#class-captureprocmemory)

see [_IgnoreEvent: dagrunner.plugin_framework.IGNORE_EVENT](dagrunner.plugin_framework.md#_ignoreevent-ignore_event)

see [class: dagrunner.plugin_framework.NodeAwarePlugin](dagrunner.plugin_framework.md#class-nodeawareplugin)

see [_SkipEvent: dagrunner.plugin_framework.SKIP_EVENT](dagrunner.plugin_framework.md#_skipevent-skip_event)

see [class: dagrunner.utils.TimeIt](dagrunner.utils.md#class-timeit)

see [function: dagrunner.utils.as_iterable](dagrunner.utils.md#function-as_iterable)

see [function: dagrunner.utils.function_to_argparse_parse_args](dagrunner.utils.md#function-function_to_argparse_parse_args)

see [module: dagrunner.utils.logger](dagrunner.utils.logger.md#module-dagrunnerutilslogger)

see [function: dagrunner.utils.networkx.visualise_graph](dagrunner.utils.networkx.md#function-visualise_graph)

## class: `ExecuteGraph`

[Source](../dagrunner/execute_graph.py#L260)

### Call Signature:

```python
ExecuteGraph(networkx_graph: str, networkx_graph_kwargs: dict = None, <function plugin_executor>, scheduler: str = 'multiprocessing', num_workers: int = 1, profiler_filepath: str = None, config_filepath: str = None, dry_run: bool = False, verbose: bool = False, **kwargs)
```

### function: `__call__`

[Source](../dagrunner/execute_graph.py#L383)

#### Call Signature:

```python
__call__(self)
```

Call self as a function.

### function: `__init__`

[Source](../dagrunner/execute_graph.py#L261)

#### Call Signature:

```python
__init__(self, networkx_graph: str, networkx_graph_kwargs: dict = None, <function plugin_executor>, scheduler: str = 'multiprocessing', num_workers: int = 1, profiler_filepath: str = None, config_filepath: str = None, dry_run: bool = False, verbose: bool = False, **kwargs)
```

Execute a networkx graph using a chosen scheduler.

Args:
- `networkx_graph` (networkx.DiGraph, callable or str):
  Python dot path to a `networkx.DiGraph` or tuple(edges, settings) object, or
  callable that returns one.  When called via the library, we support passing
  the `networkx.DiGraph` or `tuple(edges, settings)` objects directly.  Note
  that 'settings' represent a mapping (dictionary) between node and the node
  attributes.  When provided, DAGrunner will attempt to convert this tuple into
  a networkx through the following pseudo-code:
    1. Copy node identity properties into the node attributes dictionary
      and remove any attributes that are 'None' ('settings' from the tuple
      provided).
    2. Construct an empty networkx.DiGraph object.
    3. Add edges to this graph ('edges' from the tuple provided).
    4. Add node to attributes lookup to this graph ('settings' from the tuple
      provided).
    It is recommended that the user instead provide the networkx graph directly
    rather than relying on DAGrunner to decide how to construct it.
- `networkx_graph_kwargs` (dict):
  Keyword arguments to pass to the `networkx_graph` when it represents a
  callable.  Optional.
- `plugin_executor` (callable):
  A callable object that executes a plugin function or method with the provided
  arguments and keyword arguments.  By default, uses the `plugin_executor`
  function.  Optional.
- `scheduler` (str):
  Accepted values include "ray", "multiprocessing" and those recognised
  by dask: "threads", "processes" and "single-threaded" (useful for debugging)
  and "distributed".  See https://docs.dask.org/en/latest/scheduling.html.
  Optional.
- `num_workers` (int):
  Number of processes or threads to use.  Optional.
- `config_filepath` (str):
  Path to the configuration file.  See [dagrunner.config](dagrunner.config.md).
  Optional.
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

[Source](../dagrunner/execute_graph.py#L380)

#### Call Signature:

```python
visualise(self, **kwargs)
```

## dict: `SCHEDULERS`

## function: `main`

[Source](../dagrunner/execute_graph.py#L394)

### Call Signature:

```python
main()
```

Entry point of the program.
Parses command line arguments and executes the graph using the ExecuteGraph class.

## function: `plugin_executor`

[Source](../dagrunner/execute_graph.py#L43)

### Call Signature:

```python
plugin_executor(*args, call=None, verbose=False, dry_run=False, common_kwargs=None, node_id=None, **node_properties)
```

Executes a plugin callable with the provided arguments and keyword arguments.

Plugins can be functions or classes.  If a class, it is instantiated with the
keyword arguments provided in the `call` tuple.  The plugin callable is then
executed with the positional arguments provided in `args` and the keyword arguments
provided in the `call` tuple.  A plugin call is skipped if 1 or more of the `args`
is the `SKIP_EVENT` object.

Args:
- `*args`: Positional arguments to be passed to the plugin callable.
- `call`: A tuple containing the callable object (plugin) or python dot path to one
  and optionally keyword arguments on instantiating and calling to that plugin:
  - `(CallableClass, kwargs_init, kwargs_call)` -> `CallableClass(**kwargs_init)(*args, **kwargs_call)`
  - `(CallableClass, {}, kwargs_call)` -> `CallableClass()(*args, **kwargs_call)`
  - `(CallableClass)` - `CallableClass()(*args)`
  - `(callable, kwargs)` -> `callable(*args, **kwargs)`
  - `(callable)` -> `callable(*args)`
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

