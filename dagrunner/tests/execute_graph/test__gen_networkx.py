# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from dataclasses import dataclass

import networkx as nx
import pytest

from dagrunner.execute_graph import _get_networkx


@dataclass(frozen=True)
class Node:
    step: str
    leadtime: int = None


def test_get_networkx_accepts_digraph_instance():
    """A provided NetworkX graph object is returned unchanged."""
    graph = nx.DiGraph()
    graph.add_edge("a", "b")

    result = _get_networkx(graph)

    assert result is graph


def test_get_networkx_accepts_callable():
    """A callable graph factory is returned unchanged."""
    graph_factory = nx.path_graph

    result = _get_networkx(graph_factory)

    assert result is graph_factory


def test_get_networkx_resolves_dot_path_string():
    """A dot-path string resolves to a module attribute."""
    result = _get_networkx("networkx.generators.classic.path_graph")

    assert result is nx.generators.classic.path_graph


def test_get_networkx_converts_edges_and_nodes_tuple():
    """A tuple of (edges, nodes) is converted to a NetworkX DiGraph."""
    edges = [("a", "b"), ("b", "c")]
    nodes = {
        "a": {"call": "alpha"},
        "b": {"call": "beta"},
        "c": {"call": "gamma"},
    }

    result = _get_networkx((edges, nodes))

    assert isinstance(result, nx.DiGraph)
    assert set(result.edges()) == set(edges)
    assert result.nodes["a"] == {"call": "alpha"}
    assert result.nodes["b"] == {"call": "beta"}
    assert result.nodes["c"] == {"call": "gamma"}


def test_get_networkx_copies_node_properties_for_object_nodes():
    """Node object attributes are copied and None values are removed."""
    node1 = Node(step="extract", leadtime=0)
    node2 = Node(step="transform", leadtime=None)
    edges = [(node1, node2)]
    nodes = {
        node1: {"call": "do_extract"},
        node2: {"call": "do_transform"},
    }

    result = _get_networkx((edges, nodes))

    assert result.nodes[node1] == {
        "step": "extract",
        "leadtime": 0,
        "call": "do_extract",
    }
    assert result.nodes[node2] == {
        "step": "transform",
        "call": "do_transform",
    }


def test_get_networkx_rejects_unrecognised_input():
    """Invalid graph input should raise a clear ValueError."""
    with pytest.raises(ValueError, match="Not recognised 'networkx_graph' parameter"):
        _get_networkx([1, 2, 3])
