# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import json
import os
import time
from dataclasses import dataclass
from unittest import mock

import networkx as nx
import pytest

from dagrunner.config import GlobalConfiguration
from dagrunner.events import SKIP_EVENT
from dagrunner.execute_graph import ExecuteGraph
from dagrunner.plugin_framework import Input, Plugin, SaveJson
from dagrunner.utils._cache import _PickleCache

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

    def __init__(self, debug=False) -> None:
        self._debug = debug
        super().__init__()

    def __call__(self, *args, id=None):
        if self._debug:
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


@pytest.fixture()
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
        EDGES.append((node1, node2))

        # node3 -> node4
        node3 = Node(step="step3", leadtime=leadtime)
        node4 = Node(step="step4", leadtime=leadtime)
        EDGES.append((node3, node4))

        # node2 -> node5
        node5 = Node(step="step5", leadtime=leadtime)
        EDGES.append((node2, node5))

        # node4 -> node5
        node4 = Node(step="step4", leadtime=leadtime)
        EDGES.append((node4, node5))

        for nodenum in range(1, 6):
            node = vars()[f"node{nodenum}"]
            SETTINGS[node] = {
                "call": (ProcessID, None, {"id": nodenum}),
            }

        node_save = Node(step="save", leadtime=leadtime)
        EDGES.append((node5, node_save))
        output_files.append(tmp_dir / f"result_{leadtime}.json")
        # we let SaveJson expand the filepath for us from the node properties (leadtime)
        SETTINGS[node_save] = {
            "call": (
                SaveJson,
                None,
                {"filepath": f"{tmp_dir}/result_{{leadtime}}.json"},
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
    the graph has been executed correctly and respected dependencies.
    """
    # set debug to true to introduce a 'sleep' to ProcessID.  Useful for verifying rough
    # parallel execution performance.
    debug = False
    EDGES, SETTINGS, output_files = graph
    graph = ExecuteGraph(
        (EDGES, SETTINGS),
        num_workers=3,
        scheduler=scheduler,
        verbose=False,
        debug=debug,
    )()
    for output_file in output_files:
        with open(output_file, "r") as file:
            # two of them are expected since we have two leadtime branches
            res = json.load(file)
            assert res == "1_2_3_4_5"


class SkipExe(Plugin):
    def __call__(*args, **kwargs):
        return SKIP_EVENT


def test_skip_execution(graph):
    """Test plugin execution skipping."""
    # if propagation works correctly for multiprocessing then it should work for all
    scheduler = "multiprocessing"
    EDGES, SETTINGS, output_files = graph

    # skip execution of the second branch
    SETTINGS[Node(step="step2", leadtime=HOUR)] = {
        "call": (SkipExe, None, {"id": 2}),
    }
    graph = ExecuteGraph(
        (EDGES, SETTINGS),
        num_workers=3,
        scheduler=scheduler,
        verbose=False,
    )()
    output_file = output_files[0]
    with open(output_file, "r") as file:
        # two of them are expected since we have two leadtime branches
        res = json.load(file)
        assert res == "1_2_3_4_5"
    assert not os.path.exists(output_files[1])


class RaiseErr(Plugin):
    def __call__(*args, **kwargs):
        raise ValueError("some error")


def test_multiprocessing_error_handling(graph):
    """
    multiprocessing captures and provides additional context to exceptions raised.
    """
    scheduler = "multiprocessing"
    EDGES, SETTINGS, output_files = graph

    # # skip execution of the second branch
    SETTINGS[Node(step="step2", leadtime=HOUR)] = {
        "call": (RaiseErr, None, {"id": 2}),
    }
    graph = ExecuteGraph(
        (EDGES, SETTINGS),
        num_workers=3,
        scheduler=scheduler,
        verbose=False,
    )
    with pytest.raises(RuntimeError, match="RaiseErr"):
        graph()


@pytest.fixture()
def graph_input():
    SETTINGS = {}
    EDGES = []

    # node1 -> node2
    node1 = Node(step="step1", leadtime=1)
    node2 = Node(step="dummy", leadtime=1)
    EDGES.append((node1, node2))

    SETTINGS[node1] = {
        "call": (Input, None, {"filepath": "{step}_{leadtime}"}),
    }
    SETTINGS[node2] = {
        "call": (lambda x: x,),
    }
    return EDGES, SETTINGS


def test_override_node_property_with_setting(graph_input, capsys):
    scheduler = "single-threaded"
    EDGES, SETTINGS = graph_input

    new_step = "altered_step"
    SETTINGS[Node(step="step1", leadtime=1)] |= {"step": new_step}

    _ = ExecuteGraph(
        (EDGES, SETTINGS),
        num_workers=1,
        scheduler=scheduler,
        verbose=True,
    )()
    output = capsys.readouterr()
    assert f"result: {new_step}_1" in output.out


@pytest.fixture
def pickle_path():
    with mock.patch(
        "dagrunner.execute_graph.CONFIG", new=GlobalConfiguration()
    ) as patch_config:
        patch_config._config["dagrunner_runtime"]["cache_dir"] = "/dummy_path"
        patch_config._config["dagrunner_runtime"]["cache_enabled"] = True
    return


@pytest.mark.parametrize(
    "edges, exists, mtime, expected_run_nodes",
    [
        # Cache utilisation from a multiple depth graph.
        #
        # s                 skip status
        # src1->a->b->c->d
        # e                 exist status
        #
        #    s     s   s
        # (((src2->g)->h) & c)->e->f
        #    e     e   e
        [
            [
                ["src1", "a"],
                ["a", "b"],
                ["b", "c"],
                ["c", "d"],
                ["src2", "g"],
                ["g", "h"],
                ["c", "e"],
                ["e", "f"],
                ["h", "e"],
            ],
            ["src1", "src2", "g", "h"],  # files that exist
            None,  # timestamp of files that exist (None==timestamp doesn't matter)
            ["a", "b", "c", "d", "e", "f"],  # target graph nodes (filtered)
        ],
        # Cache utilisation from basic graph with timestamp.
        #
        #    s     s  s  s  skip status
        #    src1->a->b->c
        #    e     e  e  e  exist status
        #
        #    s     s
        #    src1->aa->bb->c
        #    e     e   e   e
        #
        #    s      s
        #    src2->(b & bb)
        #    e      e   e
        #
        #    s   s
        #    c->(f & g)
        #    e   e
        #
        #    s
        #    src1->d->e
        #    e        e
        [
            [
                ["b", "c"],
                ["bb", "c"],
                ["src2", "bb"],
                ["aa", "bb"],  # bb exists and src2 is newer (don't skip)
                ["src1", "aa"],  # aa exists and src1 is older (skip)
                ["src2", "b"],
                ["aa", "b"],  # b exists and src2 is older (skip)
                ["src1", "a"],  # a exists and src1 is older (skip)
                ["d", "e"],  # e exist but comes after d which doesn't (don't skip)
                ["src1", "d"],  # d doesn't exist (don't skip)
                ["c", "f"],  # f exists (don't skip)
                ["c", "g"],  # g doesn't exist (don't skip)
            ],  # edges
            ["c", "bb", "src2", "aa", "src1", "b", "a", "e", "f"],  # files that exist
            [103, 100, 101, 98, 97, 102, 99, 90, 104],  # file modified time
            ["bb", "c", "d", "e", "f", "g"],  # target graph nodes (filtered)
        ],
    ],
)
def test_cache_uitilisation_all(pickle_path, edges, exists, mtime, expected_run_nodes):
    """
    Cache utilisation

    Demonstrating that nodes are correctly skipped when their output cache files exist
    and whether their inputs timestamps are older.
    """

    nodes = [
        (node, {"call": lambda x=None, y=None: node}) for edge in edges for node in edge
    ]

    nxgraph = nx.DiGraph()
    nxgraph.add_edges_from(edges)
    nxgraph.add_nodes_from(nodes)

    # files that exist
    exists = [_PickleCache(node_id).cache_filepath for node_id in exists]
    isfile = lambda x: x in exists

    isfile_patch = mock.patch("dagrunner.runner.os.path.isfile", side_effect=isfile)

    if mtime:
        # apply timestamp
        getmtime = lambda x: {fpath: ftime for fpath, ftime in zip(exists, mtime)}[x]
        getmtime_patch = mock.patch(
            "dagrunner.runner.os.path.getmtime", side_effect=getmtime
        )
    else:
        # skip if file exists (i.e. timestamp doesn't matter)
        getmtime_patch = mock.patch("dagrunner.runner.os.path.getmtime", return_value=0)
    with isfile_patch, getmtime_patch:
        graph = ExecuteGraph(nxgraph, scheduler="single-threaded", verbose=True)
    # expecting the following nodes to still run
    assert (
        sorted(
            [graph._exec_graph[node][3]["node_id"] for node in graph._exec_graph.keys()]
        )
        == expected_run_nodes
    )
