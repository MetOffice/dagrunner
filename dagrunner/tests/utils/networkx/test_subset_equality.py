# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from collections import namedtuple
from dataclasses import dataclass

import pytest

from dagrunner.utils.networkx import subset_equality


def test_namedtuple():
    namedtuple1 = namedtuple("NamedTuple", ["a", "b", "c"])
    node = namedtuple1(a=1, b=2, c=3)

    node_pattern = namedtuple1(a=1, b=2, c=3)
    assert subset_equality(node_pattern, node) is True

    node_pattern = namedtuple1(a=1, b=2, c=None)
    assert subset_equality(node_pattern, node) is True

    node_pattern = namedtuple1(a=1, b=2, c=6)
    assert subset_equality(node_pattern, node) is False


def test_dataclass():
    @dataclass(order=True, eq=True, frozen=True)
    class Node:
        a: int = None
        b: int = None
        c: int = None

    node = Node(a=1, b=2, c=3)

    node_pattern = Node(a=1, b=2, c=3)
    assert subset_equality(node_pattern, node) is True

    node_pattern = Node(a=1, b=2, c=None)
    assert subset_equality(node_pattern, node) is True

    node_pattern = Node(a=1, b=2, c=6)
    assert subset_equality(node_pattern, node) is False


def test_other_type():
    # check warning is issued
    msg = "subset equality on incompatible object types"
    with pytest.warns(UserWarning, match=msg):
        assert subset_equality(1, 1) is True
    with pytest.warns(UserWarning, match=msg):
        assert subset_equality(1, 2) is False
