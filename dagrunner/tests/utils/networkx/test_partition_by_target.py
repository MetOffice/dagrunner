# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from dataclasses import dataclass

import networkx as nx
import pytest

from dagrunner.utils.networkx import partition_graph_by_target


@dataclass(order=True, eq=True, frozen=True)
class Node:
    d: str = None  # noqa: E740
    l: int = None  # noqa: E741
    s: int = None  # noqa: E741

    def __str__(self):
        return f"D:{self.d}_L:{self.l}_S:{self.s}"


@pytest.fixture
def graph():
    """
    A1 -> B1 -> C1

    A2 -> B2 -> C2

    D2 -> E2 -> F2
    B1 -> E2
    B2 -> E2


    """

    graph = nx.DiGraph()
    # A1 -> B1 -> C1
    a1 = Node("a", 1, 1)
    b1 = Node("a", 1, 2)
    c1 = Node("a", 1, 3)
    graph.add_edge(a1, b1)
    graph.add_edge(b1, c1)

    # A2 -> B2 -> C2
    a2 = Node("a", 2, 1)
    b2 = Node("a", 2, 2)
    c2 = Node("a", 2, 3)
    graph.add_edge(a2, b2)
    graph.add_edge(b2, c2)

    # D2 -> E2 -> F2
    d2 = Node("d", 2, 1)
    e2 = Node("e", 2, 2)
    f2 = Node("f", 2, 3)
    graph.add_edge(d2, e2)
    graph.add_edge(e2, f2)

    # B1 -> E2
    graph.add_edge(b1, e2)

    # B2 -> E2
    graph.add_edge(b2, e2)

    return graph


def test_default_targets(graph):
    subgraphs, decouple_lookup = partition_graph_by_target(
        graph, decouple_properties="l"
    )
    a1, b1, c1 = Node("a", 1, 1), Node("a", 1, 2), Node("a", 1, 3)
    a2, b2, c2 = Node("a", 2, 1), Node("a", 2, 2), Node("a", 2, 3)
    d2, e2, f2 = Node("d", 2, 1), Node("e", 2, 2), Node("f", 2, 3)

    assert set(subgraphs) == {c1, c2, f2}
    assert set(subgraphs[c1].edges) == {(a1, b1), (b1, c1)}
    assert set(subgraphs[c2].edges) == {(a2, b2), (b2, c2)}
    assert set(subgraphs[f2].edges) == {
        (d2, e2),
        (e2, f2),
        (a2, b2),
        (b2, e2),
        (b1, e2),
    }
    assert decouple_lookup == {
        c1: None,
        c2: None,
        f2: {b1: (c1,)},
    }


def test_multiple_suppliers():
    shared = Node("s", 1, 1)
    target_a, target_b, consumer = Node("a", 1, 3), Node("b", 1, 3), Node("c", 2, 1)
    graph = nx.DiGraph([(shared, target_a), (shared, target_b), (shared, consumer)])

    _, decouple_lookup = partition_graph_by_target(graph, decouple_properties="l")

    assert decouple_lookup[consumer] == {shared: (target_a, target_b)}


def test_unowned_boundary_node():
    graph = nx.DiGraph([(Node("s", 1, 1), Node("d", 2, 1))])

    with pytest.raises(ValueError, match="no supplying target"):
        partition_graph_by_target(graph, decouple_properties="l")


def test_cyclic_subgraph_dependencies():
    a1, a2, t1 = Node("a", 1, 1), Node("a", 1, 2), Node("a", 1, 3)
    b1, b2, t2 = Node("b", 2, 1), Node("b", 2, 2), Node("b", 2, 3)
    graph = nx.DiGraph([(a1, a2), (a2, t1), (b1, b2), (b2, t2), (a1, b2), (b1, a2)])

    with pytest.raises(ValueError, match="cyclic"):
        partition_graph_by_target(graph, decouple_properties="l")
