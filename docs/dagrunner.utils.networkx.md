# module: `dagrunner.utils.networkx`

[Source](../dagrunner/utils/networkx.py#L0)

see [function: dagrunner.utils.as_iterable](dagrunner.utils.md#function-as_iterable)

see [function: dagrunner.utils.subset_equality](dagrunner.utils.md#function-subset_equality)

see [module: dagrunner.utils.visualisation](dagrunner.utils.visualisation.md#module-dagrunnerutilsvisualisation)

## function: `collapse_graph`

[Source](../dagrunner/utils/networkx.py#L112)

### Call Signature:

```python
collapse_graph(graph: networkx.classes.digraph.DiGraph, collapse_properties: Union[str, Iterable[str]], collapsed_data_summary: bool = False)
```

Collapses a directed graph by grouping nodes based on specified properties.

This function modifies the input graph by collapsing nodes that share the same
values for the specified properties. It also generates mappings to track the
relationship between the collapsed nodes and the original nodes.

Args:
- `graph`: The directed graph to be collapsed. The nodes of the graph
    must be dataclass instances.
- `collapse_properties`: A single property or an iterable
    of properties to collapse the graph along. These properties must exist in the
    dataclass definition of the graph nodes.
- `collapsed_data_summary`
    Where False, the collapsed node data lookup returned is a set of all
    contributing node data dictionaries (excluding any collapse properties).
    If True, this set of dictionaries is merged into a single dictionary of value
    sets.  Useful for representing large amounts of data in a more compact form,
    at the cost of loosing associative relationship between data keys and values.


Returns:
    Tuple[nx.DiGraph, Dict[Any, Set[str]], Dict[Any, Dict[str, List[Any]]]]:
        - The collapsed graph as a new `nx.DiGraph` object.
        - A dictionary, mapping each collapsed node to a set representing the data
          across the uncollapsed node set.  See 'collapsed_data_summary' where this
          may change.
        - A dictionary mapping each collapsed node to a dictionary of the
          collapsed properties and their corresponding sorted values from
          the original nodes.

Raises:
    TypeError: If the nodes of the graph are not dataclass instances.

Notes:
- The function uses `dataclasses.replace` to create new nodes with updated
    properties for collapsing.
- The `subset_equality` function is used to determine if a node in the original
    graph matches a collapsed node.

## function: `get_subset_with_dependencies`

[Source](../dagrunner/utils/networkx.py#L50)

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

[Source](../dagrunner/utils/networkx.py#L224)

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
  'mermaid' (javascript, default) and 'matplotlib' (experimental and unsupported).
  See [visualise_graph_mermaid](#function-visualise_graph_mermaid).
- `collapse_properties`: One or more properties to collapse nodes on.  Only
  supported for nodes represented by dataclasses right now.
- `title`: The title of the visualisation.
- `output_filepath`: The output filepath to save the visualisation to.
- `**kwargs`: Additional keyword arguments to pass to the visualisation backend.
  The default and only supported backend right now (mermaid) supports the following
  keyword arguments:
  - `group_by`: One or more property to group nodes by (i.e. subgraphing)
  - `label_by`: One or more property to label visualisation nodes by.

