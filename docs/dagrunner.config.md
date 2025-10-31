# module: `dagrunner.config`

[Source](../dagrunner/config.py#L0)

This module handles the run-time configuration of the dagrunner library.

Certain hooks are present in the library for providing detailed control over
dagrunner run-time.

The configuration of dagrunner follows a first-in first-out approach on parsing
configuration options and is handled by :class:`dagrunner.config.GlobalConfiguration`.
This means that any number of configuration files can be parsed.  On import,
`dagrunner.cfg` is parsed when present in the dagrunner root folder.  Each successive
configuration file parsing will override existing parameter values.

see [class: dagrunner.utils.Singleton](dagrunner.utils.md#class-singleton)

## GlobalConfiguration: `CONFIG`

## class: `GlobalConfiguration`

[Source](../dagrunner/config.py#L28)

### Call Signature:

```python
GlobalConfiguration(*args, **kwargs)
```

The global configuration class handles any number of configuration files,
where subsequent configuration entries act to override previous entries
parsed.

All group names parsed are prefixed with "dagrunner" and all entries are then
parsed strictly.  Those groups not with this prefix are silently ignored.

The following represents a description of the runtime configuration
options::

    # Graph visualisation
    [dagrunner_visualisation]
    enabled
    title
    collapse_properties
    backend
    output_filepath
    group_by
    label_by

    [dagrunner_runtime]
    # cache disable/enable: None/False/True.
    # None implies enabled only if cache_dir is set.
    cache_enabled
    # if not specified and cache enabled, uses temp directory 'dagrunner_cache'
    # in temp folder
    cache_dir

    # Logging
    [dagrunner_logging]
    enabled
    host
    port

### function: `__getitem__`

[Source](../dagrunner/config.py#L172)

#### Call Signature:

```python
__getitem__(self, key)
```

### function: `__init__`

[Source](../dagrunner/config.py#L83)

#### Call Signature:

```python
__init__(self)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__repr__`

[Source](../dagrunner/config.py#L90)

#### Call Signature:

```python
__repr__(self)
```

Return repr(self).

### function: `__setitem__`

[Source](../dagrunner/config.py#L175)

#### Call Signature:

```python
__setitem__(self, key, value)
```

### function: `__str__`

[Source](../dagrunner/config.py#L87)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `parse_configuration`

[Source](../dagrunner/config.py#L146)

#### Call Signature:

```python
parse_configuration(self, filename)
```

Parses a new configuration file.

Entries in 'filename' override existing entries in the configuration,
while entries not set remain unchanged from the previous state.

Parameters
----------
filename : str
    Name of the configuration file to read.

