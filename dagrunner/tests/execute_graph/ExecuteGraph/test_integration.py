# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from dataclasses import dataclass
import json
import time
from unittest.mock import patch

import pytest

from dagrunner.plugin_framework import Plugin, SaveJson
from dagrunner.execute_graph import ExecuteGraph


HOUR = 3600
MINUTE = 60


# Basic processing plugin
class ProcessID(Plugin):
    """
    Concatenate node IDs together

    Most straightforward plugin possible that can demonstrate taking some input,
    modifying it and returning that updated state.  This enables us to demonstrate
    the passing of data between nodes in the graph.
    Additionally, if debug is True, sleep for 1 second to simulate a long running.
    This facilitates testing of the parallel execution of the graph.
    """

    def __call__(self, *args, id=None, debug=False):
        if debug:
            time.sleep(1)
        concat_arg_id = str(id)
        if args and args[0]:
            concat_arg_id = "_".join([str(arg) for arg in args if arg]) + f"_{id}"
        return concat_arg_id


# Basic node class
@dataclass(order=True, eq=True, frozen=True)
class Node:
    step: str = None
    leadtime: int = None

    def __str__(self):
        return f"S:{self.step}_L:{self.leadtime}"


@pytest.fixture(scope="session")
def graph(tmp_path_factory):
    leadtimes = tuple(range(0, HOUR * 2, HOUR))

    SETTINGS = {}
    EDGES = []
    output_files = []
    tmp_dir = tmp_path_factory.mktemp("dagrunner_test")

    for leadtime in leadtimes:
        # node1 -> node2
        node1 = Node(step="step1", leadtime=leadtime)
        node2 = Node(step="step2", leadtime=leadtime)
        EDGES.append([node1, node2])

        # node3 -> node4
        node3 = Node(step="step3", leadtime=leadtime)
        node4 = Node(step="step4", leadtime=leadtime)
        EDGES.append([node3, node4])

        # node2 -> node5
        node5 = Node(step="step5", leadtime=leadtime)
        EDGES.append([node2, node5])

        # node4 -> node5
        node4 = Node(step="step4", leadtime=leadtime)
        EDGES.append([node4, node5])

        for nodenum in range(1, 6):
            node = vars()[f"node{nodenum}"]
            SETTINGS[node] = {
                "call": tuple([ProcessID, {"id": nodenum, "debug": False}]),
            }

        node_save = Node(step="save", leadtime=leadtime)
        EDGES.append([node5, node_save])
        output_files.append(tmp_dir / f"result_{leadtime}.json")
        # we let SaveJson expand the filepath for us from the node properties (leadtime)
        SETTINGS[node_save] = {
            "call": tuple(
                [SaveJson, {"filepath": f"{tmp_dir}/result_{{leadtime}}.json"}]
            )
        }
    return EDGES, SETTINGS, output_files


@pytest.mark.parametrize(
    "scheduler",
    ["single-threaded", "processes", "multiprocessing", "distributed"],  # , "ray"]
)
def test_execution(graph, scheduler):
    """
    Test scheduler execution of a simple graph

    This also ensures that data is passed in memory between nodes for the range of
    schedulers being tested.  The simple graph has a SaveJson node at the end of each
    branch for recording the final state.  It is this that we verify to ensure that
    the graph has be executed correctly and respected dependencies.
    """
    # when debug==True, ProcessID does a sleep.  This is useful for testing parallel execution.
    debug = False
    EDGES, SETTINGS, output_files = graph
    with patch("dagrunner.execute_graph.logger.ServerContext"):
        graph = ExecuteGraph(
            (EDGES, SETTINGS),
            num_workers=3,
            scheduler=scheduler,
            verbose=False,
            debug=debug,
        )
        graph()
    for output_file in output_files:
        with open(output_file, "r") as file:
            # two of them are expected since we have to leadtime branches
            res = json.load(file)
            assert len(res) == 1
            assert res[0] == "1_2_3_4_5"
