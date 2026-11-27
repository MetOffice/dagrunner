# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from dataclasses import dataclass

import networkx as nx
import pytest

from dagrunner.utils.networkx import collapse_graph


@dataclass(order=True, eq=True, frozen=True)
class Node:
    diagnostic: str = None
    leadtime: int = None

    def __str__(self):
        return f"D:{self.diagnostic}_L:{self.leadtime}"


def _gen_node(diag, leadtime):
    return (
        Node(diagnostic=diag, leadtime=leadtime),
        {
            "call": (
                f"module.path.{diag}",
                {"init_arg": f"ia_{leadtime}"},
                {"call_arg": f"ca_{leadtime}"},
            ),
            "prop": f"prop_{diag}",
            "leadtime": leadtime,
            "diagnostic": diag,
        },
    )


@pytest.fixture(scope="session")
def graph():
    ngraph = nx.DiGraph()
    for leadtime in [1, 2]:
        node_a, node_a_data = _gen_node("a", leadtime)
        node_b, node_b_data = _gen_node("b", leadtime)
        ngraph.add_edge(node_a, node_b)
        ngraph.add_node(node_a, **node_a_data)
        ngraph.add_node(node_b, **node_b_data)

        node_c, node_c_data = _gen_node("c", leadtime)
        node_d, node_d_data = _gen_node("d", leadtime)
        ngraph.add_edge(node_c, node_d)
        ngraph.add_node(node_c, **node_c_data)
        ngraph.add_node(node_d, **node_d_data)

        node_e, node_e_data = _gen_node("e", leadtime)
        ngraph.add_edge(node_b, node_e)
        ngraph.add_edge(node_d, node_e)
        ngraph.add_node(node_e, **node_e_data)
    return ngraph


def test_basic(graph):
    graph, node_data_lookup, node_collapsed_lookup = collapse_graph(
        graph, collapse_properties="leadtime"
    )

    inspection_node = Node(diagnostic="a")

    # check node data lookup is correct
    assert inspection_node in node_data_lookup
    assert {
        "{'call': ('module.path.a', {'init_arg': 'ia_2'}, {'call_arg': 'ca_2'}), "
        "'prop': 'prop_a', 'diagnostic': 'a'}",
        "{'call': ('module.path.a', {'init_arg': 'ia_1'}, {'call_arg': 'ca_1'}), "
        "'prop': 'prop_a', 'diagnostic': 'a'}",
    } == node_data_lookup[inspection_node]

    # check node_collapsed_lookup is correct
    assert inspection_node in node_collapsed_lookup
    assert node_collapsed_lookup[inspection_node] == {"leadtime": [1, 2]}

    # check nodes of collapsed graph are correct
    assert set(graph.nodes) == {
        Node(diagnostic="a"),
        Node(diagnostic="b"),
        Node(diagnostic="c"),
        Node(diagnostic="d"),
        Node(diagnostic="e"),
    }
    # check data of collapsed graph are now empty (no longer applicable)
    assert inspection_node in graph.nodes
    assert {} == graph.nodes[inspection_node]


def test_collapsed_data_summary(graph):
    graph, node_data_lookup, node_collapsed_lookup = collapse_graph(
        graph, collapse_properties="leadtime", collapsed_data_summary=True
    )

    inspection_node = Node(diagnostic="a")

    # check node data lookup is correct
    assert inspection_node in node_data_lookup
    assert {
        "call": {
            "('module.path.a', {'init_arg': 'ia_1'}, {'call_arg': 'ca_1'})",
            "('module.path.a', {'init_arg': 'ia_2'}, {'call_arg': 'ca_2'})",
            "module.path.a",
        },
        "prop": {"prop_a"},
        "diagnostic": {"a"},
    } == node_data_lookup[inspection_node]

    # check node_collapsed_lookup is correct
    assert inspection_node in node_collapsed_lookup
    assert node_collapsed_lookup[inspection_node] == {"leadtime": [1, 2]}

    # check nodes of collapsed graph are correct
    assert set(graph.nodes) == {
        Node(diagnostic="a"),
        Node(diagnostic="b"),
        Node(diagnostic="c"),
        Node(diagnostic="d"),
        Node(diagnostic="e"),
    }
    # check data of collapsed graph are now empty (no longer applicable)
    assert inspection_node in graph.nodes
    assert {} == graph.nodes[inspection_node]
