# module: `dagrunner.utils.visualisation`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L0)

Module responsible for scheduler independent graph visualisation

## class: `MermaidGraph`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L55)

### Call Signature:

```python
MermaidGraph()
```

### function: `__init__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L59)

#### Call Signature:

```python
__init__(self)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L76)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `add_connection`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L73)

#### Call Signature:

```python
add_connection(self, id1, id2)
```

### function: `add_node`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L62)

#### Call Signature:

```python
add_node(self, nodeid, label=None, tooltip=None, url=None)
```

## class: `MermaidHTML`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L80)

### Call Signature:

```python
MermaidHTML(graph)
```

### function: `__init__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L126)

#### Call Signature:

```python
__init__(self, graph)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L192)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `save`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L197)

#### Call Signature:

```python
save(self, output_filepath)
```

## function: `visualise_graph`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/visualisation.py#L205)

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

