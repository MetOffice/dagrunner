# module: `dagrunner.utils.networkx`

[Source](../dagrunner/utils/networkx.py#L0)

see [class: dagrunner.utils.visualisation.HTMLTable](dagrunner.utils.visualisation.md#class-htmltable)

see [class: dagrunner.utils.visualisation.MermaidGraph](dagrunner.utils.visualisation.md#class-mermaidgraph)

see [class: dagrunner.utils.visualisation.MermaidHTML](dagrunner.utils.visualisation.md#class-mermaidhtml)

see [function: dagrunner.utils.as_iterable](dagrunner.utils.md#function-as_iterable)

see [function: dagrunner.utils.in_notebook](dagrunner.utils.md#function-in_notebook)

see [function: dagrunner.utils.subset_equality](dagrunner.utils.md#function-subset_equality)

## function: `get_subset_with_dependencies`

[Source](../dagrunner/utils/networkx.py#L55)

### Call Signature:

```python
get_subset_with_dependencies(graph: networkx.classes.digraph.DiGraph, filter_list: Union[dict, Iterable[dict]])
```

Helper function to easily filter networkx graphs.

Each item in our filter list determines whether its node should be included or
excluded.

Args:
- `graph`: The graph to filter.
- `filter_list`: The list of filters to apply.
    Each item in this list should take the form:
        {node: <node>, exclude: <bool>, descendants: <bool>, ancestors: <bool>}

## function: `visualise_graph`

[Source](../dagrunner/utils/networkx.py#L325)

### Call Signature:

```python
visualise_graph(graph: networkx.classes.digraph.DiGraph, backend: str = 'mermaid', collapse_properties: Union[str, Iterable[str]] = None, title: str = None, output_filepath: str = None, **kwargs)
```

Visualise a networkx graph.

Plots each disconnected branch of nodes with their connected edges of its own
distinct color.  Intended for plotting small graphs, whether filtered (e.g. a graph
filtered for a specific leadtime or diagnostic) and or collapsed along specified
dimensions (e.g. collapsing along the 'leadtime' property).

Args:
- `graph`: The graph to visualise.
- `backend`: The backend to use for visualisation.  Supported values include
  'mermaid' (javascript, default) and 'matplotlib'.
  See [visualise_graph_mermaid](#function-visualise_graph_mermaid).
- `collapse_properties`: One or more properties to collapse nodes on.  Only
  supported for nodes represented by dataclasses right now.
- `title`: The title of the visualisation.
- `output_filepath`: The output filepath to save the visualisation to.

## function: `visualise_graph_matplotlib`

[Source](../dagrunner/utils/networkx.py#L117)

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

[Source](../dagrunner/utils/networkx.py#L215)

### Call Signature:

```python
visualise_graph_mermaid(graph: networkx.classes.digraph.DiGraph, node_info_lookup: dict = None, title: str = None, output_filepath: str = None, group_by: Union[str, Iterable[str]] = None, label_by: Union[str, Iterable[str]] = None)
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

