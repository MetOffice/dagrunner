# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import dataclasses
import operator
from typing import Hashable, Iterable, Union

import networkx as nx

from . import as_iterable, subset_equality, visualisation


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


def _collapse_graph(graph: nx.DiGraph, collapse_properties: Union[str, Iterable[str]]):
    node_data_lookup = {}
    node_collapsed_lookup = {}
    collapse_properties = as_iterable(collapse_properties)
    if not dataclasses.is_dataclass(next(iter(graph.nodes))):
        raise TypeError(
            "Graph collapse along properties only supported for dataclasses right  now."
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
        node_collapsed_lookup[node] = {
            property: set([getattr(node, property) for node in filtered_nodes])
            for property in collapse_properties
        }
        for key in node_collapsed_lookup[node]:
            try:
                node_collapsed_lookup[node][key] = sorted(
                    node_collapsed_lookup[node][key],
                    key=lambda x: (x is None, x),
                )
            except TypeError:
                continue

        node_data_lookup[node] = set(
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
    return graph, node_data_lookup, node_collapsed_lookup


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
    """
    node_data_lookup = node_collapsed_lookup = None
    if collapse_properties:
        graph, node_data_lookup, node_collapsed_lookup = _collapse_graph(
            graph, collapse_properties
        )

    if backend == "mermaid":
        visualisation.visualise_graph_mermaid(
            graph,
            title=title,
            output_filepath=output_filepath,
            node_data_lookup=node_data_lookup,
            node_tooltip_lookup=node_collapsed_lookup,
            **kwargs,
        )
    elif backend == "matplotlib":
        node_info_lookup = None
        if collapse_properties:
            node_info_lookup = {
                key: {**node_data_lookup[key], **node_collapsed_lookup[key]}
                for key in node_data_lookup
            }
        visualisation.visualise_graph_matplotlib(
            graph,
            title=title,
            output_filepath=output_filepath,
            node_info_lookup=node_info_lookup,
            **kwargs,
        )
    else:
        raise ValueError(f"Unsupported visualisation backend: {backend}")
