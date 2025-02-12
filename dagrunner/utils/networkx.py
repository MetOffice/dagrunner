# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import dataclasses
import math
import operator
import pprint
import warnings
import webbrowser
from typing import Hashable, Iterable, Union

import networkx as nx

from . import as_iterable, in_notebook, subset_equality
from .visualisation import HTMLTable, MermaidGraph, MermaidHTML

MERMAID_SUBGRAPH_COLORS = [
    "#D4A76A",  # Muted Orange)
    "#A0C4DE",  # Muted Sky Blue)
    "#78B69A",  # Muted Green)
    "#DDD290",  # Muted Yellow)
    "#7E9ACD",  # Muted Blue)
    "#BF8163",  # Muted Vermillion)
    "#B58FA4",  # Muted Reddish Purple)
]


def _update_node_ancestry(
    graph: nx.DiGraph,
    filter_nodes: set[Hashable],
    filtered_nodes: set[Hashable] = None,
    ancestors: bool = True,
    descendants: bool = False,
    exclude: bool = False,
) -> set[Hashable]:
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
    graph: nx.DiGraph, filter_list: Union[dict, Iterable[dict]]
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
    filter_list = as_iterable(filter_list)
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

    warnings.warn(
        "This function is deprecated. Use 'mermaid' backend instead.",
        DeprecationWarning,
    )

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
    group_by: Union[str, Iterable[str]] = None,
    label_by: Union[str, Iterable[str]] = None,
):
    """
    Visualise a networkx graph using mermaid.

    Args:
    - `graph`: The graph to visualise.
    - `node_info_lookup`: A dictionary mapping nodes to their information.
    - `title`: The title of the visualisation.
    - `output_filepath`: The output filepath to save the visualisation to.
    - `group_by`: One or more property to group nodes by (i.e.
      [subgraph](https://mermaid-js.github.io/mermaid/#/subgraph)).
    - `label_by`: One or more property to label visualisation nodes by.
    """

    def gen_label(node_id, node, label_by):
        label = f"{node_id}"
        if label_by:
            for key in label_by:
                if (val := getattr(node, key)) is not None:
                    label += f"\n{key}: {val}"
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
    ):
        if node not in node_target_id_map:
            node_target_id_map[node] = node_id
            label = gen_label(node_id, node, label_by)
            tooltip = "collapsed over:\n" + "\n".join(
                map(
                    str.strip,
                    pprint.pformat(node_info_lookup[node]["collapsed"]).split("\n"),
                )
            )
            info = "\n".join(
                map(
                    str.strip,
                    pprint.pformat(node_info_lookup[node]["node data"]).split("\n"),
                )
            )
            mermaid.add_node(
                node_id,
                label=label,
                tooltip=tooltip,
            )
            table.add_row(node_id, node, tooltip, info)
            node_id += 1
        return node_id

    mermaid = MermaidGraph(title=title or "")
    table = HTMLTable(["id", "node", "collapsed", "info"])

    label_by = as_iterable(label_by)
    group_by = as_iterable(group_by)

    node_target_id_map = {}
    node_id = 0
    nodes = graph.nodes

    if group_by:
        nodes = sorted(
            graph.nodes,
            key=lambda node: [getattr(node, key, "") or "" for key in group_by],
        )

    curr_subgraphs = None
    for target in nodes:
        if group_by:
            subgraphs_raw = [getattr(target, key) for key in group_by]
            subgraphs = list(filter(None, subgraphs_raw))

            # determining whether subgraphing remains the same
            if curr_subgraphs is not None:
                len_min = min(len(curr_subgraphs), len(subgraphs))
                diff_ind = len_min
                for ind in range(len_min):
                    if curr_subgraphs[ind] != subgraphs[ind]:
                        diff_ind = ind
                        break
                indent_chng = max(0, len(curr_subgraphs) - len(subgraphs)) + (
                    len_min - diff_ind
                )
                for _ in range(indent_chng):
                    mermaid.add_raw("end")

            gen_subgraph = False
            for subg_ind, subgraph in enumerate(subgraphs):
                if gen_subgraph is False and curr_subgraphs is not None:
                    if (
                        len(curr_subgraphs) > subg_ind
                        and curr_subgraphs[subg_ind] == subgraph
                    ):
                        # same subgraph so don't redefine it
                        continue
                gen_subgraph = True

                subg_id = "_".join(subgraphs[: subg_ind + 1])
                colour_index = subgraphs_raw.index(subgraph) - 1
                if colour_index >= 0:
                    colour = MERMAID_SUBGRAPH_COLORS[
                        colour_index % len(MERMAID_SUBGRAPH_COLORS)
                    ]
                    mermaid.add_raw(f"style {subg_id} fill:{colour}")
                if subg_ind > 0:
                    mermaid.add_raw(f"subgraph {subg_id}[{subgraph}]")
                else:
                    mermaid.add_raw(f"subgraph {subg_id}")
            curr_subgraphs = subgraphs

        node_id = add_node(
            target,
            mermaid,
            table,
            node_id,
            node_target_id_map,
            node_info_lookup,
            label_by,
        )
    if group_by:
        for nesting in range(len(subg_id.split("_"))):
            mermaid.add_raw("end")

    for target in nodes:
        for pred in graph.predecessors(target):
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
    backend: str = "mermaid",
    collapse_properties: Union[str, Iterable[str]] = None,
    title: str = None,
    output_filepath: str = None,
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
      See [visualise_graph_mermaid](#function-visualise_graph_mermaid).
    - `collapse_properties`: One or more properties to collapse nodes on.  Only
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
            node_info_lookup[node] = {}
            node_info_lookup[node]["collapsed"] = {
                property: set([getattr(node, property) for node in filtered_nodes])
                for property in collapse_properties
            }
            for key in node_info_lookup[node]["collapsed"]:
                try:
                    node_info_lookup[node]["collapsed"][key] = sorted(
                        node_info_lookup[node]["collapsed"][key],
                        key=lambda x: (x is None, x),
                    )
                except TypeError:
                    continue

            node_info_lookup[node]["node data"] = set(
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
