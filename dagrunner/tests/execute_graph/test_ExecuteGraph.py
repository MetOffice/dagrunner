# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import networkx as nx

from dagrunner.execute_graph import ExecuteGraph


def test___init___graph_non_callable():
    """Passing a non-callable graph to ExecuteGraph."""
    dummy_digraph = nx.DiGraph()
    exe_graph = ExecuteGraph(dummy_digraph)
    assert exe_graph.nxgraph is dummy_digraph


def test___init___graph_callable_no_parameters():
    """Passing a callable graph to ExecuteGraph with no parameters."""
    dummy_digraph = nx.DiGraph()
    exe_graph = ExecuteGraph(lambda: dummy_digraph)
    assert exe_graph.nxgraph is dummy_digraph


def setup_graph_gen_callable(graph):
    def gen_graph(param_a, param_b):
        graph.add_nodes_from([param_a, param_b])
        return graph

    return gen_graph


def test___init___graph_callable_with_parameters():
    """Passing a callable graph to ExecuteGraph with parameters."""
    dummy_digraph = nx.DiGraph()
    graph_gen = setup_graph_gen_callable(dummy_digraph)
    exe_graph = ExecuteGraph(
        graph_gen, networkx_graph_kwargs={"param_a": "val_a", "param_b": "val_b"}
    )

    target_graph = nx.DiGraph()
    target_graph.add_nodes_from(["val_a", "val_b"])
    assert exe_graph.nxgraph is dummy_digraph
    assert dummy_digraph.nodes == target_graph.nodes
