# module: `dagrunner.utils`

[Source](../dagrunner/utils/__init__.py#L0)

see [module: _doc_styles](dagrunner.utils._doc_styles.md#module-dagrunnerutils_doc_styles)

see [module: logger](dagrunner.utils.logger.md#module-dagrunnerutilslogger)

see [module: visualisation](dagrunner.utils.visualisation.md#module-dagrunnerutilsvisualisation)

## class: `KeyValueAction`

[Source](../dagrunner/utils/__init__.py#L115)

### Call Signature:

```python
KeyValueAction(option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None)
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

[Source](../dagrunner/utils/__init__.py#L116)

#### Call Signature:

```python
__call__(self, parser, namespace, values, option_string=None)
```

Call self as a function.

## class: `ObjectAsStr`

[Source](../dagrunner/utils/__init__.py#L12)

### Call Signature:

```python
ObjectAsStr(obj, name=None)
```

Hide object under a string.

### function: `__hash__`

[Source](../dagrunner/utils/__init__.py#L24)

#### Call Signature:

```python
__hash__(self)
```

Return hash(self).

### function: `__new__`

[Source](../dagrunner/utils/__init__.py#L15)

#### Call Signature:

```python
__new__(cls, obj, name=None)
```

Create and return a new object.  See help(type) for accurate signature.

### function: `obj_to_name`

[Source](../dagrunner/utils/__init__.py#L28)

#### Call Signature:

```python
obj_to_name(obj, cls)
```

## class: `TimeIt`

[Source](../dagrunner/utils/__init__.py#L36)

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

[Source](../dagrunner/utils/__init__.py#L64)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../dagrunner/utils/__init__.py#L68)

#### Call Signature:

```python
__exit__(self, *args)
```

### function: `__init__`

[Source](../dagrunner/utils/__init__.py#L58)

#### Call Signature:

```python
__init__(self, verbose=False)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/__init__.py#L93)

#### Call Signature:

```python
__str__(self)
```

Print elapsed time in seconds.

### function: `start`

[Source](../dagrunner/utils/__init__.py#L74)

#### Call Signature:

```python
start(self)
```

### function: `stop`

[Source](../dagrunner/utils/__init__.py#L78)

#### Call Signature:

```python
stop(self)
```

## function: `docstring_parse`

[Source](../dagrunner/utils/__init__.py#L98)

### Call Signature:

```python
docstring_parse(obj)
```

## function: `function_to_argparse`

[Source](../dagrunner/utils/__init__.py#L127)

### Call Signature:

```python
function_to_argparse(func, parser=None, exclude=None)
```

Generate an argparse from a function signature

