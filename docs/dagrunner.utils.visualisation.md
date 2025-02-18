# module: `dagrunner.utils.visualisation`

[Source](../dagrunner/utils/visualisation.py#L0)

Module responsible for scheduler independent graph visualisation

## class: `HTMLTable`

[Source](../dagrunner/utils/visualisation.py#L18)

### Call Signature:

```python
HTMLTable(column_names)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L27)

#### Call Signature:

```python
__init__(self, column_names)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L39)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `add_row`

[Source](../dagrunner/utils/visualisation.py#L34)

#### Call Signature:

```python
add_row(self, *args)
```

## class: `MermaidGraph`

[Source](../dagrunner/utils/visualisation.py#L45)

### Call Signature:

```python
MermaidGraph(title=None)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L52)

#### Call Signature:

```python
__init__(self, title=None)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L76)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `add_connection`

[Source](../dagrunner/utils/visualisation.py#L73)

#### Call Signature:

```python
add_connection(self, id1, id2)
```

### function: `add_node`

[Source](../dagrunner/utils/visualisation.py#L59)

#### Call Signature:

```python
add_node(self, nodeid, label=None, tooltip=None, url=None)
```

### function: `add_raw`

[Source](../dagrunner/utils/visualisation.py#L56)

#### Call Signature:

```python
add_raw(self, raw)
```

### function: `display`

[Source](../dagrunner/utils/visualisation.py#L79)

#### Call Signature:

```python
display(self)
```

## class: `MermaidHTML`

[Source](../dagrunner/utils/visualisation.py#L112)

### Call Signature:

```python
MermaidHTML(mermaid, table=None)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L404)

#### Call Signature:

```python
__init__(self, mermaid, table=None)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L407)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `save`

[Source](../dagrunner/utils/visualisation.py#L412)

#### Call Signature:

```python
save(self, output_filepath)
```

