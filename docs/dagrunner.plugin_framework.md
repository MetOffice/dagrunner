# module: `dagrunner.plugin_framework`

[Source](../dagrunner/plugin_framework.py#L0)

see [function: dagrunner.utils.process_path](dagrunner.utils.md#function-process_path)

## class: `DataPolling`

[Source](../dagrunner/plugin_framework.py#L167)

### Call Signature:

```python
DataPolling()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L168)

#### Call Signature:

```python
__call__(self, *args, timeout=120, polling=1, file_count=None, verbose=False)
```

Poll for the availability of files

Poll for data and return when all data is available or otherwise raise an
exception if the timeout is reached.

Args:
- *args: Variable length argument list of file patterns to be checked.
  `<hostname>:<path>` syntax supported for files on a remote host.
- timeout (int): Timeout in seconds (default is 120 seconds).
- polling (int): Time interval in seconds between each poll (default is 1
  second).
- file_count (int): Expected number of files to be found for globular
    expansion (default is >= 1 files per pattern).

Returns:
- None

Raises:
- RuntimeError: If the timeout is reached before all files are found.

## class: `Input`

[Source](../dagrunner/plugin_framework.py#L268)

### Call Signature:

```python
Input()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L269)

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

[Source](../dagrunner/plugin_framework.py#L123)

### Call Signature:

```python
Load()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L141)

#### Call Signature:

```python
__call__(self, *args, staging_dir=None, verbose=False, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- staging_dir: Directory to stage files in.  If the staging directory doesn't
  exist, then create it.
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L124)

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

[Source](../dagrunner/plugin_framework.py#L302)

### Call Signature:

```python
LoadJson()
```

Load json file.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L141)

#### Call Signature:

```python
__call__(self, *args, staging_dir=None, verbose=False, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- staging_dir: Directory to stage files in.  If the staging directory doesn't
  exist, then create it.
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L305)

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

[Source](../dagrunner/plugin_framework.py#L341)

### Call Signature:

```python
LoadPickle()
```

Load pickle file.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L141)

#### Call Signature:

```python
__call__(self, *args, staging_dir=None, verbose=False, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- staging_dir: Directory to stage files in.  If the staging directory doesn't
  exist, then create it.
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L344)

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

[Source](../dagrunner/plugin_framework.py#L42)

### Call Signature:

```python
NodeAwarePlugin()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L23)

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

[Source](../dagrunner/plugin_framework.py#L20)

### Call Signature:

```python
Plugin()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L23)

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

## class: `SaveJson`

[Source](../dagrunner/plugin_framework.py#L313)

### Call Signature:

```python
SaveJson()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L314)

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

[Source](../dagrunner/plugin_framework.py#L352)

### Call Signature:

```python
SavePickle()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L353)

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

[Source](../dagrunner/plugin_framework.py#L50)

### Call Signature:

```python
Shell()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L51)

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

