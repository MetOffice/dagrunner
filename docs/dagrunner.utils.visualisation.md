# module: `dagrunner.utils.visualisation`

[Source](../dagrunner/utils/visualisation.py#L0)

Module responsible for scheduler independent graph visualisation

see [function: dagrunner.utils.as_iterable](dagrunner.utils.md#function-as_iterable)

see [function: dagrunner.utils.in_notebook](dagrunner.utils.md#function-in_notebook)

## class: `HTMLTable`

[Source](../dagrunner/utils/visualisation.py#L43)

### Call Signature:

```python
HTMLTable(column_names)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L52)

#### Call Signature:

```python
__init__(self, column_names)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L71)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `add_row`

[Source](../dagrunner/utils/visualisation.py#L61)

#### Call Signature:

```python
add_row(self, *args, id=None)
```

## list: `MERMAID_SUBGRAPH_COLORS`

## class: `MermaidGraph`

[Source](../dagrunner/utils/visualisation.py#L77)

### Call Signature:

```python
MermaidGraph(title=None)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L84)

#### Call Signature:

```python
__init__(self, title=None)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L108)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `add_connection`

[Source](../dagrunner/utils/visualisation.py#L105)

#### Call Signature:

```python
add_connection(self, id1, id2)
```

### function: `add_node`

[Source](../dagrunner/utils/visualisation.py#L91)

#### Call Signature:

```python
add_node(self, nodeid, label=None, tooltip=None, url=None)
```

### function: `add_raw`

[Source](../dagrunner/utils/visualisation.py#L88)

#### Call Signature:

```python
add_raw(self, raw)
```

### function: `display`

[Source](../dagrunner/utils/visualisation.py#L111)

#### Call Signature:

```python
display(self)
```

## class: `MermaidHTML`

[Source](../dagrunner/utils/visualisation.py#L144)

### Call Signature:

```python
MermaidHTML(mermaid, table=None)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L176)

#### Call Signature:

```python
__init__(self, mermaid, table=None)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L179)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `save`

[Source](../dagrunner/utils/visualisation.py#L186)

#### Call Signature:

```python
save(self, output_filepath)
```

## str: `WEBCOMPONENT_PATH`

## function: `visualise_graph_matplotlib`

[Source](../dagrunner/utils/visualisation.py#L194)

### Call Signature:

```python
visualise_graph_matplotlib(graph: networkx.classes.digraph.DiGraph, node_info_lookup: dict = None, title: str = None, output_filepath: str = None)
```

Visualise a networkx graph using matplotlib.

Note that this backend is provided as-is and not intended for production use.
'mermaid' graph is the recommended approach to graph visualisation.

Args:
- `graph`: The graph to visualise.
- `node_info_lookup`: A dictionary mapping nodes to their information.
- `title`: The title of the visualisation.
- `output_filepath`: The output filepath to save the visualisation to.

## function: `visualise_graph_mermaid`

[Source](../dagrunner/utils/visualisation.py#L334)

### Call Signature:

```python
visualise_graph_mermaid(graph: networkx.classes.digraph.DiGraph, node_data_lookup: dict = None, node_tooltip_lookup: dict = None, title: str = None, output_filepath: str = None, group_by: Union[str, Iterable[str]] = None, label_by: Union[str, Iterable[str]] = None)
```

Visualise a networkx graph using mermaid.

Args:
- `graph`: The graph to visualise.
- `node_info_lookup`: A dictionary mapping nodes to their information.
- `title`: The title of the visualisation.
- `output_filepath`: The output filepath to save the visualisation to.
- `group_by`: One or more property to group nodes by (i.e.
  [subgraph](https://mermaid-js.github.io/mermaid/#/subgraph)).
- `label_by`: One or more property to label visualisation nodes by.

