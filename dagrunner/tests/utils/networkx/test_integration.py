# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import inspect
import tempfile
from dataclasses import dataclass
from unittest import mock

import networkx as nx
import pytest

from dagrunner.tests import assert_text_file_equal
from dagrunner.utils.networkx import visualise_graph


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
                {"init_arg": f"ia_{diag}"},
                {"call_arg": f"ca_{diag}"},
            ),
            "prop": f"prop_{diag}",
            "leadtime": leadtime,
            "diagnostic": diag,
        },
    )


def assert_visual(graph, backend, **kwargs):
    caller_frame = inspect.stack()[1]
    func_name = caller_frame.function
    module = inspect.getmodule(caller_frame.frame)
    module_name = module.__name__ if module else "<unknown>"

    with tempfile.TemporaryDirectory() as tmpdirname:
        output_filepath = f"{tmpdirname}/graph.html"
        visualise_graph(
            graph, backend="mermaid", output_filepath=output_filepath, **kwargs
        )
        assert_text_file_equal(output_filepath, f"{module_name}.{func_name}.html")


@pytest.fixture(scope="session")
def graph(tmp_path_factory):
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
    assert_visual(graph, "mermaid")


def test_collapse_properties(graph):
    assert_visual(graph, "mermaid", collapse_properties=("leadtime",))


def test_groupby(graph):
    assert_visual(graph, "mermaid", group_by="diagnostic")


def test_groupby_recursive(graph):
    from collections import namedtuple

    Node = namedtuple("Node", ["diagnostic", "model", "step"])
    graph = nx.DiGraph()
    a = Node("a", "bb", "aaa")
    b = Node("a", "bb", "bbb")
    c = Node("x", "bb", "aaa")
    d = Node("a", "xx", "aaa")
    e = Node("z", "zz", "zzz")
    f = Node("y", None, "zzz")
    g = Node("None", "cc", "zzz")

    graph.add_edge(a, b)
    graph.add_edge(b, c)
    graph.add_edge(c, d)
    graph.add_edge(d, e)
    graph.add_edge(e, f)
    graph.add_edge(f, g)
    assert_visual(graph, "mermaid", group_by=["diagnostic", "model"])


def test_special_characters_words(graph):
    # Ensure we support labels containing 'interpolate'.  For some reason this causes
    # an error in mermaid.  Putting double quotes around this fixes the issue.
    # dummy_callable =
    for leadtime in [1, 2]:
        node_a, node_a_data = _gen_node("a", leadtime)
        # This is the special word so must be quoted within the html.
        node_a_data["testparam"] = "interpolate"
        node_a_data["call"] = list(node_a_data["call"])
        # Common characters that need to be escaped (non-exhaustive).
        node_a_data["call"][0] = (
            "<function test_basic.<locals>.<lambda> at 0x7f04ce115048>"
        )
        node_a_data["call"] = tuple(node_a_data["call"])
        graph.add_node(node_a, **node_a_data)

    assert_visual(graph, "mermaid")


def test_properties_of_none(graph):
    # label should not display properties of None (less information is more useful)
    node_z, node_z_data = _gen_node("z", None)
    graph.add_node(node_z, **node_z_data)
    assert_visual(graph, "mermaid", label_by=["diagnostic", "leadtime"])


def test_node_properties_unsortable_types(graph):
    # Mixed types that are not sortable
    # Here we assign a diagnostic name of integer 0 while the remaining nodes remain
    # are strings.
    node_0, node_0_data = _gen_node(0, 1)
    graph.add_node(node_0, **node_0_data)

    with mock.patch(
        "dagrunner.utils.visualisation.visualise_graph_mermaid"
    ) as mock_mermaid:
        visualise_graph(
            graph,
            backend="mermaid",
            output_filepath=mock.sentinel.output_filepath,
            collapse_properties=["diagnostic"],
        )
    mock_mermaid.assert_called_once()


@pytest.fixture
def mock_mpl_backend():
    with mock.patch(
        "dagrunner.utils.visualisation.visualise_graph_matplotlib"
    ) as mock_backend:
        yield mock_backend


def test_basic_matplotlib_backend(graph, mock_mpl_backend):
    # check that the matplotlib backend is called but that's all
    visualise_graph(
        graph, backend="matplotlib", output_filepath=mock.sentinel.output_filepath
    )
    mock_mpl_backend.assert_called_once()
