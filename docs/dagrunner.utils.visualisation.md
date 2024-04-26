# module: `dagrunner.utils.visualisation`

[Source](../dagrunner/utils/visualisation.py#L0)

Module responsible for scheduler independent graph visualisation

# class: `MermaidGraph`

[Source](../dagrunner/utils/visualisation.py#L54)

# class: `MermaidHTML`

[Source](../dagrunner/utils/visualisation.py#L79)

# function: `visualise_graph`

[Source](../dagrunner/utils/visualisation.py#L202)

Args:
    graph (dict):
        Graph with keys representing 'targets' and values representing
        (function, *args).
    output_filepath (str):
        Node graph visualisation html output filepath.

Returns:
    None:

