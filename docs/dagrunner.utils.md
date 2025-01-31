# module: `dagrunner.utils`

[Source](../dagrunner/utils/__init__.py#L0)

see [module: _doc_styles](dagrunner.utils._doc_styles.md#module-dagrunnerutils_doc_styles)

see [module: logger](dagrunner.utils.logger.md#module-dagrunnerutilslogger)

see [module: networkx](dagrunner.utils.networkx.md#module-dagrunnerutilsnetworkx)

see [module: visualisation](dagrunner.utils.visualisation.md#module-dagrunnerutilsvisualisation)

## class: `CaptureProcMemory`

[Source](../dagrunner/utils/__init__.py#L216)

### Call Signature:

```python
CaptureProcMemory(interval=1.0, pid=None)
```

Capture maximum process memory statistics.

See `get_proc_mem_stat` for more information.

### function: `__enter__`

[Source](../dagrunner/utils/__init__.py#L197)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../dagrunner/utils/__init__.py#L202)

#### Call Signature:

```python
__exit__(self, exc_type, exc_value, traceback)
```

### function: `__init__`

[Source](../dagrunner/utils/__init__.py#L227)

#### Call Signature:

```python
__init__(self, interval=1.0, pid=None)
```

Initialize the memory capture.

Args:
- `interval`: Time interval in seconds to capture memory statistics.
  Note that memory statistics are captured by reading /proc files.  It is
  advised not to reduce the interval too much, otherwise we increase the
  overhead of reading the files.
- `pid`: Process id.  Optional.  Default is the current process.

### function: `max`

[Source](../dagrunner/utils/__init__.py#L206)

#### Call Signature:

```python
max(self)
```

Return maximum memory statistics.

Returns:
- Dictionary with memory statistics in MB.

## class: `CaptureSysMemory`

[Source](../dagrunner/utils/__init__.py#L268)

### Call Signature:

```python
CaptureSysMemory(interval=1.0, **kwargs)
```

Capture maximum system memory statistics.

See `get_sys_mem_stat` for more information.

### function: `__enter__`

[Source](../dagrunner/utils/__init__.py#L197)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../dagrunner/utils/__init__.py#L202)

#### Call Signature:

```python
__exit__(self, exc_type, exc_value, traceback)
```

### function: `__init__`

[Source](../dagrunner/utils/__init__.py#L165)

#### Call Signature:

```python
__init__(self, interval=1.0, **kwargs)
```

Initialize the memory capture.

Args:
- `interval`: Time interval in seconds to capture memory statistics.
  Note that memory statistics are captured by reading `/proc` files.  It is
  advised not to reduce the interval too much, otherwise we increase the
  overhead of reading the files.

### function: `max`

[Source](../dagrunner/utils/__init__.py#L206)

#### Call Signature:

```python
max(self)
```

Return maximum memory statistics.

Returns:
- Dictionary with memory statistics in MB.

## class: `KeyValueAction`

[Source](../dagrunner/utils/__init__.py#L386)

### Call Signature:

```python
KeyValueAction(option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None, deprecated=False)
```

Information about how to convert command line strings to Python objects.

Action objects are used by an ArgumentParser to represent the information
needed to parse a single argument from one or more strings from the
command line. The keyword arguments to the Action constructor are also
all attributes of Action instances.

Keyword Arguments:

    - option_strings -- A list of command-line option strings which
        should be associated with this action.

    - dest -- The name of the attribute to hold the created object(s)

    - nargs -- The number of command-line arguments that should be
        consumed. By default, one argument will be consumed and a single
        value will be produced.  Other values include:
            - N (an integer) consumes N arguments (and produces a list)
            - '?' consumes zero or one arguments
            - '*' consumes zero or more arguments (and produces a list)
            - '+' consumes one or more arguments (and produces a list)
        Note that the difference between the default and nargs=1 is that
        with the default, a single value will be produced, while with
        nargs=1, a list containing a single value will be produced.

    - const -- The value to be produced if the option is specified and the
        option uses an action that takes no values.

    - default -- The value to be produced if the option is not specified.

    - type -- A callable that accepts a single string argument, and
        returns the converted value.  The standard Python types str, int,
        float, and complex are useful examples of such callables.  If None,
        str is used.

    - choices -- A container of values that should be allowed. If not None,
        after a command-line argument has been converted to the appropriate
        type, an exception will be raised if it is not a member of this
        collection.

    - required -- True if the action must always be specified at the
        command line. This is only meaningful for optional command-line
        arguments.

    - help -- The help string describing the argument.

    - metavar -- The name to be used for the option's argument with the
        help string. If None, the 'dest' value will be used as the name.

### function: `__call__`

[Source](../dagrunner/utils/__init__.py#L387)

#### Call Signature:

```python
__call__(self, parser, namespace, values, option_string=None)
```

Call self as a function.

## class: `ObjectAsStr`

[Source](../dagrunner/utils/__init__.py#L280)

### Call Signature:

```python
ObjectAsStr(obj, name=None)
```

Hide object under a string.

### function: `__hash__`

[Source](../dagrunner/utils/__init__.py#L294)

#### Call Signature:

```python
__hash__(self)
```

Return hash(self).

### function: `__new__`

[Source](../dagrunner/utils/__init__.py#L285)

#### Call Signature:

```python
__new__(cls, obj, name=None)
```

Create and return a new object.  See help(type) for accurate signature.

### function: `obj_to_name`

[Source](../dagrunner/utils/__init__.py#L298)

#### Call Signature:

```python
obj_to_name(obj, cls)
```

## class: `Singleton`

[Source](../dagrunner/utils/__init__.py#L101)

Singleton metaclass.

### function: `__call__`

[Source](../dagrunner/utils/__init__.py#L108)

#### Call Signature:

```python
__call__(cls, *args, **kwargs)
```

Call self as a function.

## class: `TimeIt`

[Source](../dagrunner/utils/__init__.py#L306)

### Call Signature:

```python
TimeIt(verbose=False)
```

Timer context manager which can also be used as a standalone timer.

We can query our timer for the elapsed time in seconds even before .

Example as a context manager:

    >>> with TimeIt() as timer:
    >>>     sleep(0.05)
    >>> print(timer)
    "Elapsed time: 0.05s"

Example as a standalone timer:

    >>> timer = TimeIt()
    >>> timer.start_timer()
    >>> sleep(0.05)
    >>> print(timer)
    "Elapsed time: 0.05s"

### function: `__enter__`

[Source](../dagrunner/utils/__init__.py#L335)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../dagrunner/utils/__init__.py#L339)

#### Call Signature:

```python
__exit__(self, *args)
```

### function: `__init__`

[Source](../dagrunner/utils/__init__.py#L329)

#### Call Signature:

```python
__init__(self, verbose=False)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/__init__.py#L364)

#### Call Signature:

```python
__str__(self)
```

Print elapsed time in seconds.

### function: `start`

[Source](../dagrunner/utils/__init__.py#L345)

#### Call Signature:

```python
start(self)
```

### function: `stop`

[Source](../dagrunner/utils/__init__.py#L349)

#### Call Signature:

```python
stop(self)
```

## function: `as_iterable`

[Source](../dagrunner/utils/__init__.py#L93)

### Call Signature:

```python
as_iterable(obj)
```

## function: `data_polling`

[Source](../dagrunner/utils/__init__.py#L487)

### Call Signature:

```python
data_polling(*args, timeout=120, polling=1, file_count=None, fail_fast=True, verbose=False)
```

Poll for the availability of files

Poll for data and return when all data is available or otherwise raise an
exception if the timeout is reached.

Args:
- *args: Variable length argument list of file patterns to be checked.
    `<hostname>:<path>` syntax supported for files on a remote host.

Args:
- timeout (int): Timeout in seconds (default is 120 seconds).
- polling (int): Time interval in seconds between each poll (default is 1
    second).
- file_count (int): Expected number of files to be found for globular
    expansion (default is >= 1 files per pattern).
- fail_fast (bool): Stop when a file is not found (default is True).
- verbose (bool): Print verbose output.

## function: `docstring_parse`

[Source](../dagrunner/utils/__init__.py#L369)

### Call Signature:

```python
docstring_parse(obj)
```

## function: `function_to_argparse`

[Source](../dagrunner/utils/__init__.py#L398)

### Call Signature:

```python
function_to_argparse(func, parser=None, exclude=None)
```

Generate an argparse from a function signature

## function: `function_to_argparse_parse_args`

[Source](../dagrunner/utils/__init__.py#L475)

### Call Signature:

```python
function_to_argparse_parse_args(*args, **kwargs)
```

## function: `get_proc_mem_stat`

[Source](../dagrunner/utils/__init__.py#L134)

### Call Signature:

```python
get_proc_mem_stat(pid=None)
```

Get process memory statistics from /proc/<pid>/status.

More information can be found at
https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.txt

Args:
- `pid`: Process id.  Optional.  Default is the current process.

Returns:
- Dictionary with memory statistics in MB.  Fields are VmSize, VmRSS, VmPeak and
  VmHWM.

## function: `get_sys_mem_stat`

[Source](../dagrunner/utils/__init__.py#L242)

### Call Signature:

```python
get_sys_mem_stat()
```

Get system memory statistics from /proc/meminfo.

More information can be found at
https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.txt

Returns:
- Dictionary with memory statistics in MB.  Fields are Committed_AS, MemFree,
  Buffers, Cached and MemTotal.

## function: `in_notebook`

[Source](../dagrunner/utils/__init__.py#L81)

### Call Signature:

```python
in_notebook()
```

Determine whether we are in a Jupyter notebook.

## function: `pairwise`

[Source](../dagrunner/utils/__init__.py#L59)

### Call Signature:

```python
pairwise(iterable)
```

Return successive overlapping pairs taken from the input iterable.

The number of 2-tuples in the output iterator will be one fewer than the
number of inputs. It will be empty if the input iterable has fewer than
two values.

pairwise('ABCDEFG') → AB BC CD DE EF FG

## function: `process_path`

[Source](../dagrunner/utils/__init__.py#L114)

### Call Signature:

```python
process_path(fpath: str)
```

Process path.

Args:
- `fpath`: Remote path in the format <host>:<path>.  If host corresponds to
  the local host, then the host element will be removed.

Returns:
- Processed path

## function: `stage_to_dir`

[Source](../dagrunner/utils/__init__.py#L672)

### Call Signature:

```python
stage_to_dir(*args, staging_dir, verbose=False)
```

Copy input filepaths to a staging area and update paths.

Hard link copies are preferred (same host) and physical copies are made otherwise.
File name, size and modification time are used to evaluate if the destination file
exists already (matching criteria of rsync).  If exists already, skip the copy.
Staged files are named: `<modification-time>_<file-size>_<filename>` to avoid
collision with identically names files.

## function: `subset_equality`

[Source](../dagrunner/utils/__init__.py#L25)

### Call Signature:

```python
subset_equality(obj_a, obj_b)
```

Return whether obj_a is a subset of obj_b.

Supporting namedtuple and dataclasses, otherwise fallback to equality.  Note that
a 'None' value in obj_a is considered a wildcard.

