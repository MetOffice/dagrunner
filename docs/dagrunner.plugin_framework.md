# module: `dagrunner.plugin_framework`

[Source](../dagrunner/plugin_framework.py#L0)

## class: `DataPolling`

[Source](../dagrunner/plugin_framework.py#L62)

### Call Signature:

```python
DataPolling()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L63)

#### Call Signature:

```python
__call__(self, *args, timeout=120, polling=1, file_count=None, verbose=False)
```

Poll for availability of files

Poll for data and return when all are available or otherwise raise an
exception if the timeout is reached.

Args:
- *args: Variable length argument list of file patterns to be checked.
- timeout (int): Timeout in seconds (default is 120 seconds).
- polling (int): Time interval in seconds between each poll (default is 1
  second).
- file_count (int): Expected number of files to be found (default is None).
    If specified, the total number of files found can be greater than the
    number of arguments.  Each argument is expected to return a minimum of
    1 match each in either case.

Returns:
- None

Raises:
- RuntimeError: If the timeout is reached before all files are found.

## class: `Input`

[Source](../dagrunner/plugin_framework.py#L118)

### Call Signature:

```python
Input()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L119)

#### Call Signature:

```python
__call__(self, *args, filepath=None, **kwargs)
```

Given a filepath, expand it and return this string

Expand the provided filepath using the keyword arguments and environment
variables.  Note that this plugin is 'node aware' since it is derived from the
`NodeAwarePlugin`.

Args:
- *args: Positional arguments are not accepted.
- filepath (str): The filepath to be expanded.
- **kwargs: Keyword arguments to be used in the expansion.  Node
  properties/attributes are additionally included here as a node aware plugin.

Returns:
- str: The expanded filepath.

Raises:
- ValueError: If positional arguments are provided.

## class: `NodeAwarePlugin`

[Source](../dagrunner/plugin_framework.py#L36)

### Call Signature:

```python
NodeAwarePlugin()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L17)

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

[Source](../dagrunner/plugin_framework.py#L14)

### Call Signature:

```python
Plugin()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L17)

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

[Source](../dagrunner/plugin_framework.py#L153)

### Call Signature:

```python
SaveJson()
```

An abstract base class plugin that is of type that instructs the plugin
executor to pass it node parameters.  This enables the definition of plugins
that are 'node aware'.

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L154)

#### Call Signature:

```python
__call__(self, *args, filepath=None, node_properties=None, **kwargs)
```

Save data to a JSON file

Save the provided data to a JSON file at the specified filepath.  The filepath
is expanded using the keyword arguments and environment variables.  Note that
this plugin is 'node aware' since it is derived from the `NodeAwarePlugin`.

Args:
- *args: Positional arguments (data) to be saved.
- filepath (str): The filepath to save the data to.
- data (Any): The data to be saved.
- **kwargs: Keyword arguments to be used in the expansion.  Node
  properties/attributes are additionally included here as a node aware plugin.

Returns:
- None

## class: `Shell`

[Source](../dagrunner/plugin_framework.py#L44)

### Call Signature:

```python
Shell()
```

Abstract base class to define our plugin UI

### function: `__call__`

[Source](../dagrunner/plugin_framework.py#L45)

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

