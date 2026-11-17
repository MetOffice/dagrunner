# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from dataclasses import dataclass

import networkx as nx
import pytest

from dagrunner.utils.networkx import partition_graph_by_target
from dagrunner.utils.visualisation import visualise_graph_mermaid


@dataclass(order=True, eq=True, frozen=True)
class Node:
    name: str = None
    d: int = None
    l: int = None
    s: int = None

    def __str__(self):
        return f"{self.name}_D:{self.d}_L:{self.l}_S:{self.s}"


@pytest.fixture
def graph():
    """
    A1 -> B1 -> C1 -> D1
    E1 -> C1

    B1 -> B2
    C1 -> C2
    A2 -> B2 -> C2 -> D2

    """

    graph = nx.DiGraph()
    a1 = Node("a1", 1, 1, 1)
    b1 = Node("b1", 1, 1, 2)
    c1 = Node("c1", 1, 2, 3)
    d1 = Node("d1", 1, 1, 4)
    e1 = Node("e1", 1, 2, 5)
    b2 = Node("b2", 2, 2, 1)
    c2 = Node("c2", 2, 2, 2)
    a2 = Node("a2", 2, 2, 3)
    d2 = Node("d2", 2, 2, 4)
    node_lookup = {
        "a1": a1,
        "b1": b1,
        "c1": c1,
        "d1": d1,
        "e1": e1,
        "b2": b2,
        "c2": c2,
        "a2": a2,
        "d2": d2,
    }

    graph.add_edge(a1, b1)
    graph.add_edge(b1, c1)
    graph.add_edge(c1, d1)
    graph.add_edge(e1, c1)

    graph.add_edge(b1, b2)
    graph.add_edge(c1, c2)
    graph.add_edge(a2, b2)
    graph.add_edge(b2, c2)
    graph.add_edge(c2, d2)

    return graph, node_lookup


def test_default_targets(graph):
    graph, node_lookup = graph
    subgraphs = partition_graph_by_target(graph)
    d1 = node_lookup["d1"]  # target1
    d2 = node_lookup["d2"]  # target2
    visualise_graph_mermaid(
        subgraphs[d1], output_filepath="subgraph_d1.md"
    )  # , label_by='name')
    visualise_graph_mermaid(
        subgraphs[d2], output_filepath="subgraph_d2.md"
    )  # , label_by='name')
    # open subgraph_d2.mmd to view the visualisation in vscode
    # import subprocess
    # subprocess.run(["code", "subgraph_d2.md"])
    a = 1
