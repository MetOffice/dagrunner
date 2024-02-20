# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'pp_systems_framework' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import tempfile

from dagrunner.utils import ObjectAsStr
from dagrunner.utils.visualisation import visualise_graph
from dagrunner.tests import assert_text_file_equal


def test_basic():
    # lambda x: x  # we don't actually define a callable as that would have a
    # changing obj ID.
    dummy_callable = "<function test_basic.<locals>.<lambda> at 0x7f04ce115048>"
    graph = {
        "target1": [
            dummy_callable,
            ObjectAsStr("target1"),
            "improver",
            "plugin1",
            "--operation",
            "A",
            "target2",
            "target3",
            "--output",
            ObjectAsStr("target1"),
        ],
        "target2": [
            dummy_callable,
            ObjectAsStr("target2"),
            "improver",
            "plugin1",
            "--operation",
            "B",
            "target3",
            "target4",
            "--output",
            ObjectAsStr("target2"),
        ],
        "target5": [
            dummy_callable,
            ObjectAsStr("target5"),
            "improver",
            "plugin2",
            "--operation",
            "C",
            "target2",
            "--output",
            ObjectAsStr("target5"),
        ],
    }
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_filepath = f"{tmpdirname}/graph.html"
        visualise_graph(graph, output_filepath)
        assert_text_file_equal(output_filepath, "dag_graph.html")


def test_label_interpolate():
    # Ensure we support labels containing 'interpolate'.  For some reason this causes
    # an error in mermaid.  Putting double quotes around this fixes the issue.
    dummy_callable = "<function test_basic.<locals>.<lambda> at 0x7f04ce115048>"
    graph = {
        "target1": [dummy_callable, ObjectAsStr("target1"), "improver", "interpolate"],
    }
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_filepath = f"{tmpdirname}/graph.html"
        visualise_graph(graph, output_filepath)
        assert_text_file_equal(output_filepath, "dag_graph_special_label.html")
