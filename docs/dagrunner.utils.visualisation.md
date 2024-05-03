# module: `dagrunner.utils.visualisation`

[Source](../dagrunner/utils/visualisation.py#L0)

Module responsible for scheduler independent graph visualisation

## class: `MermaidGraph`

[Source](../dagrunner/utils/visualisation.py#L54)

### Call Signature:

```python
MermaidGraph()
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L58)

#### Call Signature:

```python
__init__(self)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L75)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `add_connection`

[Source](../dagrunner/utils/visualisation.py#L72)

#### Call Signature:

```python
add_connection(self, id1, id2)
```

### function: `add_node`

[Source](../dagrunner/utils/visualisation.py#L61)

#### Call Signature:

```python
add_node(self, nodeid, label=None, tooltip=None, url=None)
```

## class: `MermaidHTML`

[Source](../dagrunner/utils/visualisation.py#L79)

### Call Signature:

```python
MermaidHTML(graph)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L125)

#### Call Signature:

```python
__init__(self, graph)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L189)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `save`

[Source](../dagrunner/utils/visualisation.py#L194)

#### Call Signature:

```python
save(self, output_filepath)
```

## function: `visualise_graph`

[Source](../dagrunner/utils/visualisation.py#L202)

### Call Signature:

```python
visualise_graph(graph, output_filepath)
```

Args:
    graph (dict):
        Graph with keys representing 'targets' and values representing
        (function, *args).
    output_filepath (str):
        Node graph visualisation html output filepath.

Returns:
    None:

