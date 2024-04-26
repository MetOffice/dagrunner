# module: `dagrunner.utils.visualisation`

[Source](../dagrunner/utils/visualisation.py#L0)

Module responsible for scheduler independent graph visualisation

# class: `MermaidGraph`

[Source](../dagrunner/utils/visualisation.py#L54)

### Call Signature:

```python
MermaidGraph()
```

# class: `MermaidHTML`

[Source](../dagrunner/utils/visualisation.py#L79)

### Call Signature:

```python
MermaidHTML(graph)
```

# function: `visualise_graph`

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

