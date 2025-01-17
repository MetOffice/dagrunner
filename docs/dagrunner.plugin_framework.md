# module: `dagrunner.plugin_framework`

[Source](../dagrunner/plugin_framework.py#L0)

see [class: dagrunner.utils.Singleton](dagrunner.utils.md#class-singleton)

see [function: dagrunner.utils.data_polling](dagrunner.utils.md#function-data_polling)

see [function: dagrunner.utils.process_path](dagrunner.utils.md#function-process_path)

see [function: dagrunner.utils.stage_to_dir](dagrunner.utils.md#function-stage_to_dir)

## class: `DataPolling`

[Source](../dagrunner/plugin_framework.py#L176)

### Call Signature:

```python
DataPolling(timeout=120, polling=1, file_count=None, verbose=False)
```

A trigger plugin that completes when data is successfully polled.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L185)

#### Call Signature:

```python
__call__(self, *args)
```

The main method of the plugin (abstract method).

Positional arguments represent the plugin's inputs (dependencies),
while keyword arguments represent the plugin's parameters.

Args:
- *args: Positional arguments.
- **kwargs: Keyword arguments.

Returns:
- Any: The output of the plugin.

### function: `__init__`

[Source](../dagrunner/plugin_framework.py#L179)

#### Call Signature:

```python
__init__(self, timeout=120, polling=1, file_count=None, verbose=False)
```

Initialize self.  See help(type(self)) for accurate signature.

## _IgnoreEvent: `IGNORE_EVENT`

## class: `Input`

[Source](../dagrunner/plugin_framework.py#L206)

### Call Signature:

```python
Input()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L207)

#### Call Signature:

```python
__call__(self, filepath, node_properties=None, **kwargs)
```

Given a string, expand it and return this expanded string.

Expand the provided string (typically representing a filepath) using the
keyword arguments and environment variables.  Note that this plugin is
'node aware' since it is derived from the `NodeAwarePlugin`.

Args:
- `filepath` (str): The filepath to be expanded.
- `node_properties`: node properties passed by the plugin executor.
- **kwargs: Keyword arguments to be used in the expansion.

Returns:
- str: The expanded filepath.

Raises:
- ValueError: If positional arguments are provided.

## class: `Load`

[Source](../dagrunner/plugin_framework.py#L102)

### Call Signature:

```python
Load(staging_dir=None, ignore_missing=False, verbose=False)
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L134)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- **kwargs: Keyword arguments to pass to.

### function: `__init__`

[Source](../dagrunner/plugin_framework.py#L103)

#### Call Signature:

```python
__init__(self, staging_dir=None, ignore_missing=False, verbose=False)
```

Load data from a file.

The `load` method must be implemented by the subclass.

Args:
- staging_dir: Directory to stage files in.
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L117)

#### Call Signature:

```python
load(self, *args, **kwargs)
```

Load data from a file.

Args:
- *args: Positional arguments.
- **kwargs: Keyword arguments.

Returns:
- Any: The loaded data.

Raises:
- NotImplementedError: If the method is not implemented.

## class: `LoadJson`

[Source](../dagrunner/plugin_framework.py#L240)

### Call Signature:

```python
LoadJson(staging_dir=None, ignore_missing=False, verbose=False)
```

Load json file.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L134)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- **kwargs: Keyword arguments to pass to.

### function: `__init__`

[Source](../dagrunner/plugin_framework.py#L103)

#### Call Signature:

```python
__init__(self, staging_dir=None, ignore_missing=False, verbose=False)
```

Load data from a file.

The `load` method must be implemented by the subclass.

Args:
- staging_dir: Directory to stage files in.
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L243)

#### Call Signature:

```python
load(self, *args)
```

Load data from a file.

Args:
- *args: Positional arguments.
- **kwargs: Keyword arguments.

Returns:
- Any: The loaded data.

Raises:
- NotImplementedError: If the method is not implemented.

## class: `LoadPickle`

[Source](../dagrunner/plugin_framework.py#L279)

### Call Signature:

```python
LoadPickle(staging_dir=None, ignore_missing=False, verbose=False)
```

Load pickle file.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L134)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- **kwargs: Keyword arguments to pass to.

### function: `__init__`

[Source](../dagrunner/plugin_framework.py#L103)

#### Call Signature:

```python
__init__(self, staging_dir=None, ignore_missing=False, verbose=False)
```

Load data from a file.

The `load` method must be implemented by the subclass.

Args:
- staging_dir: Directory to stage files in.
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L282)

#### Call Signature:

```python
load(self, *args)
```

Load data from a file.

Args:
- *args: Positional arguments.
- **kwargs: Keyword arguments.

Returns:
- Any: The loaded data.

Raises:
- NotImplementedError: If the method is not implemented.

## class: `NodeAwarePlugin`

[Source](../dagrunner/plugin_framework.py#L76)

### Call Signature:

```python
NodeAwarePlugin()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L57)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

The main method of the plugin (abstract method).

Positional arguments represent the plugin's inputs (dependencies),
while keyword arguments represent the plugin's parameters.

Args:
- *args: Positional arguments.
- **kwargs: Keyword arguments.

Returns:
- Any: The output of the plugin.

## class: `Plugin`

[Source](../dagrunner/plugin_framework.py#L54)

### Call Signature:

```python
Plugin()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L57)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

The main method of the plugin (abstract method).

Positional arguments represent the plugin's inputs (dependencies),
while keyword arguments represent the plugin's parameters.

Args:
- *args: Positional arguments.
- **kwargs: Keyword arguments.

Returns:
- Any: The output of the plugin.

## _SkipEvent: `SKIP_EVENT`

## class: `SaveJson`

[Source](../dagrunner/plugin_framework.py#L251)

### Call Signature:

```python
SaveJson()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L252)

#### Call Signature:

```python
__call__(self, *args, filepath, node_properties=None, **kwargs)
```

Save data to a JSON file

Save the provided data to a JSON file at the specified filepath.  The filepath
is expanded using the keyword arguments and environment variables.  Note that
this plugin is 'node aware' since it is derived from the `NodeAwarePlugin`.

Args:
- `*args`: Positional arguments (data) to be saved.
- `filepath`: The filepath to save the data to.
- `node_properties`: node properties passed by the plugin executor.
- `**kwargs`: Keyword arguments to be used in the expansion.

Returns:
- None

## class: `SavePickle`

[Source](../dagrunner/plugin_framework.py#L290)

### Call Signature:

```python
SavePickle()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L291)

#### Call Signature:

```python
__call__(self, *args, filepath, node_properties=None, **kwargs)
```

Save data to a Pickle file

Save the provided data to a pickle file at the specified filepath.  The filepath
is expanded using the keyword arguments and environment variables.  Note that
this plugin is 'node aware' since it is derived from the `NodeAwarePlugin`.

Args:
- `*args`: Positional arguments (data) to be saved.
- `filepath`: The filepath to save the data to.
- `node_properties`: node properties passed by the plugin executor.
- `**kwargs`: Keyword arguments to be used in the expansion.

Returns:
- None

## class: `Shell`

[Source](../dagrunner/plugin_framework.py#L84)

### Call Signature:

```python
Shell()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L85)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

Execute a subprocess command.

Args:
- *args: The command to be executed.
- **kwargs: Additional keyword arguments to be passed to `subprocess.run`

Returns:
- CompletedProcess: An object representing the completed process.

Raises:
- CalledProcessError: If the command returns a non-zero exit status.

