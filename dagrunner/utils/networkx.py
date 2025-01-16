# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import dataclasses
import math
import operator
import pprint
import webbrowser
from typing import Iterable
import warnings

import networkx as nx

from . import as_iterable, in_notebook
from .visualisation import HTMLTable, MermaidGraph, MermaidHTML
from . import subset_equality


def _update_node_ancestry(
    graph: nx.DiGraph,
    filter_nodes: Iterable,
    filtered_nodes: Iterable = None,
    ancestors: bool = True,
    descendants: bool = False,
    exclude: bool = False,
) -> Iterable:
    """
    Helper function to easily filter networkx graphs.

    Args:
    - `graph`: The graph to filter.
    - `filter_nodes`: The nodes to filter.
    - `filtered_nodes`: The nodes to filter from.
    - `ancestors`: Whether to include ancestors.
    - `descendants`: Whether to include descendants.
    - `exclude`: Whether to exclude the nodes (inclusion otherwise).
    """
    if filtered_nodes is None:
        filtered_nodes = set([])
    op = operator.ior if not exclude else operator.isub
    filtered_nodes = op(filtered_nodes, filter_nodes)  # +/- filtered nodes
    if descendants or ancestors:
        for node in filter_nodes:
            if descendants:
                filtered_nodes = op(
                    filtered_nodes, set(nx.descendants(graph, node))
                )  # +/- descendants of node
            if ancestors:
                filtered_nodes = op(
                    filtered_nodes, set(nx.ancestors(graph, node))
                )  # +/- ancestors of node
    return filtered_nodes


def get_subset_with_dependencies(
    graph: nx.DiGraph, filter_list: Iterable
) -> nx.DiGraph:
    """
    Helper function to easily filter networkx graphs.

    Each item in our filter list determines whether its node should be included or
    excluded.

    Args:
    - `graph`: The graph to filter.
    - `filter_list`: The list of filters to apply.
        Each item in this list should take the form:
            {node: <node>, exclude: <bool>, descendants: <bool>, ancestors: <bool>}
    """
    include_subset = [
        pattern for pattern in filter_list if not pattern.get("exclude", False)
    ]
    exclude_subset = [
        pattern for pattern in filter_list if pattern.get("exclude", False)
    ]

    # include filter
    ##################
    if include_subset:
        dependencies = set([])
        for pattern in include_subset:
            node_pattern = pattern["node"]
            filtered_nodes = set(
                filter(lambda node: subset_equality(node_pattern, node), graph.nodes)
            )
            _update_node_ancestry(
                graph,
                filtered_nodes,
                dependencies,
                exclude=False,
                descendants=pattern.get("descendants", False),
                ancestors=pattern.get("ancestors", True),
            )
        # Find non-zero offset nodes: these aren't explicitly connected their zero
        # offset versions so need to be explicitly included.
        offset_nodes = set(
            [
                dataclasses.replace(node, cycle_offset=None)
                for node in filter(
                    lambda node: node.cycle_offset is not None, dependencies
                )
            ]
        )
        offset_nodes = set(filter(lambda node: node in graph.nodes, offset_nodes))
        _update_node_ancestry(
            graph, offset_nodes, dependencies, descendants=False, ancestors=True
        )
    else:
        # include all nodes
        dependencies = set(graph.nodes)

    # exclude filter
    ##################
    for pattern in exclude_subset:
        node_pattern = pattern["node"]
        filtered_nodes = set(
            filter(lambda node: subset_equality(node_pattern, node), dependencies)
        )
        _update_node_ancestry(
            graph,
            filtered_nodes,
            dependencies,
            exclude=True,
            descendants=pattern.get("descendants", False),
            ancestors=pattern.get("ancestors", False),
        )
    return graph.subgraph(dependencies)


def visualise_graph_matplotlib(
    graph: nx.DiGraph,
    node_info_lookup: dict = None,
    title: str = None,
    output_filepath: str = None,
):
    """
    Visualise a networkx graph using matplotlib.

    Note that this backend is provided as-is and not intended for production use.
    'mermaid' graph is the recommended approach to graph visualisation.

    Args:
    - `graph`: The graph to visualise.
    - `node_info_lookup`: A dictionary mapping nodes to their information.
    - `title`: The title of the visualisation.
    - `output_filepath`: The output filepath to save the visualisation to.
    """
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseButton
    warnings.warn("This function is deprecated. Use 'mermaid' backend instead.", DeprecationWarning)

    pos = nx.spring_layout(graph, seed=42, k=8 / math.sqrt(graph.order()))

    plt.figure()
    plt.title(title)

    # Draw nodes
    nx.draw_networkx_nodes(graph, pos)

    # Get connected components
    components = nx.weakly_connected_components(graph)

    # Define a color palette with more distinct colours
    color_palette = [
        "red",
        "green",
        "blue",
        "orange",
        "purple",
        "yellow",
        "cyan",
        "magenta",
    ]

    # Draw each disconnected graph component with a different color from the palette
    for i, component in enumerate(components):
        color = color_palette[i % len(color_palette)]
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=[
                (u, v) for u, v in graph.edges() if u in component and v in component
            ],
            edge_color=color,
            arrowstyle="->",
            arrowsize=20,
        )

        # Highlight starting and termination nodes
        sources = {node for node in component if graph.in_degree(node) == 0}
        targets = {node for node in component if graph.out_degree(node) == 0}
        nx.draw_networkx_nodes(
            graph, pos, nodelist=sources, node_color="green", node_size=200
        )
        nx.draw_networkx_nodes(
            graph, pos, nodelist=targets, node_color="red", node_size=200
        )

    # Draw labels
    nx.draw_networkx_labels(graph, pos, font_size=6, font_color="black")

    # Capture clicks on nodes
    def on_click(event):
        if event.button is MouseButton.LEFT and event.inaxes:
            x, y = event.xdata, event.ydata
            for node, (nx, ny) in pos.items():
                if (x - nx) ** 2 + (y - ny) ** 2 < 0.05:  # Click radius threshold
                    print(f"Node clicked: {node}")
                    if node_info_lookup:
                        for key, val in node_info_lookup[node].items():
                            print(f"\t'{key}': {val}")
                    break

    # Connect the event handler
    fig = plt.gcf()
    fig.canvas.mpl_connect("button_press_event", on_click)

    if output_filepath:
        plt.savefig(output_filepath)
    else:
        plt.show()


def visualise_graph_mermaid(
    graph: nx.DiGraph,
    node_info_lookup: dict = None,
    title: str = None,
    output_filepath: str = None,
    group_by: str = None,
    label_by: Iterable = None,
):
    """
    Visualise a networkx graph using matplotlib.

    Args:
    - `graph`: The graph to visualise.
    - `node_info_lookup`: A dictionary mapping nodes to their information.
    - `title`: The title of the visualisation.
    - `output_filepath`: The output filepath to save the visualisation to.
    """

    def gen_label(node_id, node, label_by):
        label = f"{node_id}"
        if label_by:
            for key in label_by:
                label += f"\n{key}: {getattr(node, key)}"
        else:
            label += f"\n{str(node)}"
        return label

    def add_node(
        node,
        mermaid,
        table,
        node_id,
        node_target_id_map,
        node_info_lookup,
        label_by,
        group_by,
    ):
        if node not in node_target_id_map:
            node_target_id_map[node] = node_id
            label = gen_label(node_id, node, label_by)
            tooltip = '\n'.join(map(str.strip, pprint.pformat(node_info_lookup[node]).split('\n')))

            subgraphs = [
                getattr(node, key) for key in group_by if getattr(node, key, None)
            ]
            for subgraph in subgraphs:
                mermaid.add_raw(f"subgraph {subgraph}")
            mermaid.add_node(
                node_id,
                label=label,
                tooltip=tooltip,
            )
            for subgraph in subgraphs:
                mermaid.add_raw("end")
            table.add_row(node_id, node, tooltip)
            node_id += 1
        return node_id

    mermaid = MermaidGraph(title=title or "")
    table = HTMLTable(["id", "node", "info"])

    label_by = as_iterable(label_by)
    group_by = as_iterable(group_by)

    node_target_id_map = {}
    node_id = 0
    for target in graph.nodes:
        node_id = add_node(
            target,
            mermaid,
            table,
            node_id,
            node_target_id_map,
            node_info_lookup,
            label_by,
            group_by,
        )

        for pred in graph.predecessors(target):
            node_id = add_node(
                pred,
                mermaid,
                table,
                node_id,
                node_target_id_map,
                node_info_lookup,
                label_by,
                group_by,
            )
            mermaid.add_connection(node_target_id_map[pred], node_target_id_map[target])

    if output_filepath:
        MermaidHTML(mermaid, table).save(output_filepath)
    else:
        if in_notebook():
            mermaid.display()
        else:
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
                MermaidHTML(mermaid, table).save(f.name)
                webbrowser.open(f.name)


def visualise_graph(
    graph: nx.DiGraph,
    backend="mermaid",
    collapse_properties: Iterable = None,
    title=None,
    output_filepath=None,
    **kwargs,
):
    """
    Visualise a networkx graph.

    Plots each disconnected branch of nodes with their connected edges of its own
    distinct color.  Intended for plotting small graphs, whether filtered (e.g. a graph
    filtered for a specific leadtime or diagnostic) and or collapsed along specified
    dimensions (e.g. collapsing along the 'leadtime' property).

    Args:
    - `graph`: The graph to visualise.
    - `backend`: The backend to use for visualisation.  Supported values include
      'mermaid' (javascript, default) and 'matplotlib'.
    - `collapse_properties`: A list of properties to collapse nodes on.  Only
      supported for nodes represented by dataclasses right now.
    - `title`: The title of the visualisation.
    - `output_filepath`: The output filepath to save the visualisation to.
    """
    node_info_lookup = {}
    if collapse_properties:
        collapse_properties = as_iterable(collapse_properties)
        if not dataclasses.is_dataclass(next(iter(graph.nodes))):
            raise TypeError(
                "Graph collapse along properties only supported for dataclasses right "
                " now."
            )

        collapse_properties = {property: None for property in collapse_properties}
        collapsed_graph = nx.relabel_nodes(
            graph,
            {
                node: dataclasses.replace(node, **collapse_properties)
                for node in graph.nodes
            },
        )

        for node in collapsed_graph.nodes:
            filtered_nodes = set(
                filter(lambda gnode: subset_equality(node, gnode), graph.nodes)
            )
            node_info_lookup[node] = {
                property: sorted(
                    set([getattr(node, property) for node in filtered_nodes]),
                    key=lambda x: (x is None, x),
                )
                for property in collapse_properties
            }
            node_info_lookup[node].update({
                "node data": set(
                    [
                        str(
                            {
                                key: val
                                for key, val in graph.nodes(data=True)[gnode].items()
                                if key not in collapse_properties
                            }
                        )
                        for gnode in filtered_nodes
                    ]
                )
            })
        graph = collapsed_graph
    else:
        for node, data in graph.nodes(data=True):
            node_info_lookup[node] = {"node data": data}

    if backend == "mermaid":
        visualise_graph_mermaid(
            graph, node_info_lookup, title, output_filepath, **kwargs
        )
    elif backend == "matplotlib":
        visualise_graph_matplotlib(
            graph, node_info_lookup, title, output_filepath, **kwargs
        )
    else:
        raise ValueError(f"Unsupported visualisation backend: {backend}")
