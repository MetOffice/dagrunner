# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import warnings

import networkx as nx
import pytest

from dagrunner.utils.networkx import get_subset_with_dependencies


@pytest.fixture()
def graph():
    """
    7----|
         |
    1 -> 2--|
            |-> 5 -> 6
    3 -> 4--|        |
                     |
    8 ----- > 9----->|
              |
    10 -> 11->|
    """
    digraph = nx.DiGraph()
    digraph.add_edge(7, 2)
    digraph.add_edge(1, 2)
    digraph.add_edge(3, 4)
    digraph.add_edge(8, 9)
    digraph.add_edge(10, 11)
    digraph.add_edge(2, 5)
    digraph.add_edge(4, 5)
    digraph.add_edge(5, 6)
    digraph.add_edge(9, 6)
    return digraph


@pytest.mark.parametrize(
    "filters, target",
    [
        (
            {"node": 5, "exclude": False, "descendants": False, "ancestors": False},
            [5],
        ),
        (
            {"node": 5, "exclude": False, "descendants": True, "ancestors": False},
            [5, 6],
        ),
        (
            {"node": 5, "exclude": False, "descendants": False, "ancestors": True},
            [1, 2, 3, 4, 5, 7],
        ),
        (
            {"node": 5, "exclude": True, "descendants": False, "ancestors": False},
            [1, 2, 3, 4, 6, 7, 8, 9, 10, 11],
        ),
        (
            {"node": 5, "exclude": True, "descendants": True, "ancestors": False},
            [1, 2, 3, 4, 7, 8, 9, 10, 11],
        ),
        (
            {"node": 5, "exclude": True, "descendants": False, "ancestors": True},
            [6, 8, 9, 10, 11],
        ),
    ],
    ids=["fff", "ftf", "fft", "tff", "ttf", "tft"],
)
def test_filters(graph, filters, target):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = get_subset_with_dependencies(graph, [filters])
    assert set(res.nodes) == set(target)
