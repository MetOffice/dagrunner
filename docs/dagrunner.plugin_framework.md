# module: `dagrunner.plugin_framework`

[Source](../dagrunner/plugin_framework.py#L0)

see [function: dagrunner.utils.data_polling](dagrunner.utils.md#function-data_polling)

see [module: dagrunner.events](dagrunner.events.md#module-dagrunnerevents)

see [function: dagrunner.utils.process_path](dagrunner.utils.md#function-process_path)

see [function: dagrunner.utils.stage_to_dir](dagrunner.utils.md#function-stage_to_dir)

## class: `DataPolling`

[Source](../dagrunner/plugin_framework.py#L176)

### Call Signature:

```python
DataPolling(timeout=120, polling=1, file_count=None, verbose=False)
```

A trigger plugin that completes only when data is successfully polled.

Remote file paths using `<hostname>:<path>` syntax are supported as well as
local and remote glob patterns.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L201)

#### Call Signature:

```python
__call__(self, *args)
```

Poll for data until available or timeout is reached.

Args:
- *args: File paths or glob patterns to poll for.

Returns:
- None

### function: `__init__`

[Source](../dagrunner/plugin_framework.py#L184)

#### Call Signature:

```python
__init__(self, timeout=120, polling=1, file_count=None, verbose=False)
```

Initialize the DataPolling plugin.

Args:
- timeout (int): Maximum time to wait for data in seconds.
- polling (int): Polling interval in seconds.
- file_count (int or None): Expected number of files.
  If None, any number greater than 1 per input/glob pattern is not considered
  missing.
- verbose (bool): Whether to print verbose output.

## class: `Input`

[Source](../dagrunner/plugin_framework.py#L222)

### Call Signature:

```python
Input()
```

A plugin to expand filepaths using keyword arguments and environment variables.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L227)

#### Call Signature:

```python
__call__(self, filepath, node_properties=None, **kwargs)
```

Expand a filepath.

Expand the provided string (typically representing a filepath) using the
keyword arguments and environment variables.  Note that this plugin is
'node aware' since it is derived from the
[NodeAwarePlugin](dagrunner.plugin_framework.md#class-nodeawareplugin).

Args:
- `filepath` (str): The filepath to be expanded.
- `node_properties`: node properties passed by the plugin executor.
- **kwargs: Keyword arguments to be used in the expansion.

Returns:
- str: The expanded filepath.

Raises:
- ValueError: If positional arguments are provided.

## class: `Load`

[Source](../dagrunner/plugin_framework.py#L68)

### Call Signature:

```python
Load(staging_dir=None, on_missing='error', verbose=False)
```

Abstract data loader.

The `load` method must be implemented by the subclass.
This abstract class handles staging of files from remote hosts
and handling missing files according to the `on_missing` parameter as well
as globbing of file paths (local or remote).

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L119)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- **kwargs: Keyword arguments to pass to.

Returns:
- Any: User overrode 'load' abstractmethod return value, or
  `events.IGNORE` or `events.SKIP` if files are missing and
  `on_missing` is set to 'ignore' or 'skip' respectively.

Raises:
- FileNotFoundError: If any of the files do not exist and `on_missing` is set
  to 'error'.

### function: `__init__`

[Source](../dagrunner/plugin_framework.py#L78)

#### Call Signature:

```python
__init__(self, staging_dir=None, on_missing='error', verbose=False)
```

Load data from a file.

Args:
- staging_dir: Local directory to stage files in.
  Staging of remote files where filepaths are of `<hostname>:<path>` syntax.
  A staging directory must be specified when loading remote files.
- on_missing: Action to take when files are missing. Accepted values: 'error',
  'ignore' and 'skip'.
  'ignore' and 'skip' will return `events.IGNORE` and `events.SKIP`
  respectively, whilst 'error' will raise a `FileNotFoundError`.
  See [dagrunner.events](dagrunner.events.md)
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L102)

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

[Source](../dagrunner/plugin_framework.py#L261)

### Call Signature:

```python
LoadJson(staging_dir=None, on_missing='error', verbose=False)
```

json file loader.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L119)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- **kwargs: Keyword arguments to pass to.

Returns:
- Any: User overrode 'load' abstractmethod return value, or
  `events.IGNORE` or `events.SKIP` if files are missing and
  `on_missing` is set to 'ignore' or 'skip' respectively.

Raises:
- FileNotFoundError: If any of the files do not exist and `on_missing` is set
  to 'error'.

### function: `__init__`

[Source](../dagrunner/plugin_framework.py#L78)

#### Call Signature:

```python
__init__(self, staging_dir=None, on_missing='error', verbose=False)
```

Load data from a file.

Args:
- staging_dir: Local directory to stage files in.
  Staging of remote files where filepaths are of `<hostname>:<path>` syntax.
  A staging directory must be specified when loading remote files.
- on_missing: Action to take when files are missing. Accepted values: 'error',
  'ignore' and 'skip'.
  'ignore' and 'skip' will return `events.IGNORE` and `events.SKIP`
  respectively, whilst 'error' will raise a `FileNotFoundError`.
  See [dagrunner.events](dagrunner.events.md)
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L264)

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

[Source](../dagrunner/plugin_framework.py#L305)

### Call Signature:

```python
LoadPickle(staging_dir=None, on_missing='error', verbose=False)
```

pickle file loader.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L119)

#### Call Signature:

```python
__call__(self, *args, **kwargs)
```

Load data from a file or list of files.

Args:
- *args: List of filepaths to load. `<hostname>:<path>` syntax supported
  for loading files from a remote host.
- **kwargs: Keyword arguments to pass to.

Returns:
- Any: User overrode 'load' abstractmethod return value, or
  `events.IGNORE` or `events.SKIP` if files are missing and
  `on_missing` is set to 'ignore' or 'skip' respectively.

Raises:
- FileNotFoundError: If any of the files do not exist and `on_missing` is set
  to 'error'.

### function: `__init__`

[Source](../dagrunner/plugin_framework.py#L78)

#### Call Signature:

```python
__init__(self, staging_dir=None, on_missing='error', verbose=False)
```

Load data from a file.

Args:
- staging_dir: Local directory to stage files in.
  Staging of remote files where filepaths are of `<hostname>:<path>` syntax.
  A staging directory must be specified when loading remote files.
- on_missing: Action to take when files are missing. Accepted values: 'error',
  'ignore' and 'skip'.
  'ignore' and 'skip' will return `events.IGNORE` and `events.SKIP`
  respectively, whilst 'error' will raise a `FileNotFoundError`.
  See [dagrunner.events](dagrunner.events.md)
- verbose: Print verbose output.

### function: `load`

[Source](../dagrunner/plugin_framework.py#L308)

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

[Source](../dagrunner/plugin_framework.py#L274)

### Call Signature:

```python
SaveJson()
```

Save data to a JSON file.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L277)

#### Call Signature:

```python
__call__(self, *args, filepath, node_properties=None, **kwargs)
```

Save data to a JSON file

Save the provided data to a JSON file at the specified filepath.  The filepath
is expanded using the keyword arguments and environment variables.  Note that
this plugin is 'node aware' since it is derived from the
[NodeAwarePlugin](dagrunner.plugin_framework.md#class-nodeawareplugin).

Args:
- `*args`: Positional arguments (data) to be saved.
- `filepath`: The filepath to save the data to.
- `node_properties`: node properties passed by the plugin executor.
- `**kwargs`: Keyword arguments to be used in the expansion.

Returns:
- None

## class: `SavePickle`

[Source](../dagrunner/plugin_framework.py#L316)

### Call Signature:

```python
SavePickle()
```

Save data to a Pickle file.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L319)

#### Call Signature:

```python
__call__(self, *args, filepath, node_properties=None, **kwargs)
```

Save data to a Pickle file

Save the provided data to a pickle file at the specified filepath.  The filepath
is expanded using the keyword arguments and environment variables.  Note that
this plugin is 'node aware' since it is derived from the
[NodeAwarePlugin](dagrunner.plugin_framework.md#class-nodeawareplugin).

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

