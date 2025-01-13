# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from dataclasses import dataclass
import tempfile

import pytest
import networkx as nx

from dagrunner.tests import assert_text_file_equal
from dagrunner.utils import ObjectAsStr
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
        {"call":(f"module.path.{diag}",
                 {"init_arg": f"ia_{diag}"},
                 {"call_arg": f"ca_{diag}"}),
         "prop": f"prop_{diag}",
         "leadtime": leadtime,
         "diagnostic": diag}
    )


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
    #dummy_callable = "<function test_basic.<locals>.<lambda> at 0x7f04ce115048>"
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_filepath = f"{tmpdirname}/graph.html"
        visualise_graph(graph, backend="mermaid", output_filepath=output_filepath)
        assert_text_file_equal(output_filepath, "dag_graph.html")


def test_collapse_properties(graph):
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_filepath = f"{tmpdirname}/graph.html"
        visualise_graph(graph, backend="mermaid", output_filepath=output_filepath,
                        collapse_properties=("leadtime",))
        assert_text_file_equal(output_filepath, "dag_graph_collapsed_leadtime.html")


def test_groupby(graph):
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_filepath = f"{tmpdirname}/graph.html"
        visualise_graph(graph, backend="mermaid", output_filepath=output_filepath,
                        group_by="diagnostic")
        assert_text_file_equal(output_filepath, "dag_graph_groupby_diagnostic.html")

# def test_label_interpolate():
#     # Ensure we support labels containing 'interpolate'.  For some reason this causes
#     # an error in mermaid.  Putting double quotes around this fixes the issue.
#     dummy_callable = "<function test_basic.<locals>.<lambda> at 0x7f04ce115048>"
#     graph = {
#         "target1": [dummy_callable, ObjectAsStr("target1"), "improver", "interpolate"],
#     }
#     with tempfile.TemporaryDirectory() as tmpdirname:
#         output_filepath = f"{tmpdirname}/graph.html"
#         visualise_graph(graph, output_filepath)
#         assert_text_file_equal(output_filepath, "dag_graph_special_label.html")
