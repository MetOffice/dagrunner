# module: `dagrunner.utils.visualisation`

[Source](../dagrunner/utils/visualisation.py#L0)

Module responsible for scheduler independent graph visualisation

see [function: dagrunner.utils.as_iterable](dagrunner.utils.md#function-as_iterable)

see [function: dagrunner.utils.in_notebook](dagrunner.utils.md#function-in_notebook)

## class: `HTMLTable`

[Source](../dagrunner/utils/visualisation.py#L44)

### Call Signature:

```python
HTMLTable(column_names)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L53)

#### Call Signature:

```python
__init__(self, column_names)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L72)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `add_row`

[Source](../dagrunner/utils/visualisation.py#L62)

#### Call Signature:

```python
add_row(self, *args, id=None)
```

## list: `MERMAID_SUBGRAPH_COLORS`

## str: `MERMAID_SUBGRAPH_COLOR_HIGHLIGHT`

## class: `MermaidGraph`

[Source](../dagrunner/utils/visualisation.py#L78)

### Call Signature:

```python
MermaidGraph(title=None)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L85)

#### Call Signature:

```python
__init__(self, title=None)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L109)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `add_connection`

[Source](../dagrunner/utils/visualisation.py#L106)

#### Call Signature:

```python
add_connection(self, id1, id2)
```

### function: `add_node`

[Source](../dagrunner/utils/visualisation.py#L92)

#### Call Signature:

```python
add_node(self, nodeid, label=None, tooltip=None, url=None)
```

### function: `add_raw`

[Source](../dagrunner/utils/visualisation.py#L89)

#### Call Signature:

```python
add_raw(self, raw)
```

### function: `base64`

[Source](../dagrunner/utils/visualisation.py#L112)

#### Call Signature:

```python
base64(self)
```

### function: `display`

[Source](../dagrunner/utils/visualisation.py#L130)

#### Call Signature:

```python
display(self, output_filepath: str = None)
```

## class: `MermaidHTML`

[Source](../dagrunner/utils/visualisation.py#L156)

### Call Signature:

```python
MermaidHTML(mermaid, table=None)
```

### function: `__init__`

[Source](../dagrunner/utils/visualisation.py#L179)

#### Call Signature:

```python
__init__(self, mermaid, table=None)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `__str__`

[Source](../dagrunner/utils/visualisation.py#L182)

#### Call Signature:

```python
__str__(self)
```

Return str(self).

### function: `save`

[Source](../dagrunner/utils/visualisation.py#L189)

#### Call Signature:

```python
save(self, output_filepath)
```

## str: `WEBCOMPONENT_PATH`

## function: `visualise_graph_matplotlib`

[Source](../dagrunner/utils/visualisation.py#L197)

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

[Source](../dagrunner/utils/visualisation.py#L341)

### Call Signature:

```python
visualise_graph_mermaid(graph: networkx.classes.digraph.DiGraph, node_data_lookup: dict = None, node_tooltip_lookup: dict = None, title: str = None, output_filepath: str = None, group_by: Union[str, Iterable[str]] = None, label_by: Union[str, Iterable[str]] = None)
```

Visualise a networkx graph using mermaid.

Args:
- `graph`: The graph to visualise.
- `node_info_lookup`: A dictionary mapping nodes to their information.
- `title`: The title of the visualisation.
- `output_filepath`: The output filepath to save the visualisation to.  Where not
  provided, write a html file to a temporary location and open it with your default
  browser.  Otherwise, supported extensions include ".html", ".png", ".jpg",
  ".jpeg", ".svg" and ".md".  Note that not all formats support the full
  set of visualisation features, so html is recommended.
- `group_by`: One or more property to group nodes by (i.e.
  [subgraph](https://mermaid-js.github.io/mermaid/#/subgraph)).
- `label_by`: One or more property to label visualisation nodes by.

