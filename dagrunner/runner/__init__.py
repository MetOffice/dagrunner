# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import os

from dask.core import get_deps

from dagrunner.utils._cache import _PickleCache


def _handle_clobber(dask_graph, verbose=False):
    """
    Skip commands (nodes) in the graph.

    This function is described by the following pseudo-code::

        for branch in graph:
          # Iterate over nodes in our branch from the starting node to
          # termination node.
          for node in branch:
            if ((output of this node (command) already exists) AND
                   (input sources have modified timestamp older than output)):
                skip node
            else:
                do not skip
                Mark all node successor dependencies as 'do not skip'
                break

    """

    def get_node_id(node):
        # return node id from the tokenised node name
        return dask_graph[node][3]["node_id"]

    def get_node_args_id(node):
        # return node positional args from the tokenised node name
        return [get_node_id(arg) for arg in dask_graph[node][2]]

    pred_deps, succ_deps = get_deps(dask_graph)
    starting_nodes = []
    for tgt, deps in pred_deps.items():
        if not deps:
            starting_nodes.append(tgt)

    mark_removal = {}

    def mark_recursively_false(node):
        mark_removal[node] = False
        for successor_node in succ_deps[node]:
            mark_recursively_false(successor_node)

    def recursive_node_removal(node):
        if node in mark_removal and mark_removal[node] is False:
            mark_recursively_false(node)
            return

        # If target exists and inputs are older, then mark as skip.
        node_id = get_node_id(node)
        node_path = _PickleCache(node_id).cache_filepath
        if os.path.isfile(node_path):
            skip_key = True
            out_modtime = os.path.getmtime(node_path)
            args = get_node_args_id(node)
            for arg in args:
                arg_path = _PickleCache(arg).cache_filepath
                if (
                    os.path.isfile(arg_path)
                    and os.path.getmtime(arg_path) > out_modtime
                ):
                    skip_key = False
                    break
            if skip_key:
                # Skip node
                mark_removal[node] = True
                # Recursively eval. successor nodes for removal
                for successor_node in succ_deps[node]:
                    recursive_node_removal(successor_node)
            else:
                mark_recursively_false(node)

    # Loop over each starting node, skip nodes with pre-existing targets until
    # the task which isn't skipped in that branch.
    for starting_node in starting_nodes:
        recursive_node_removal(starting_node)
    for node, remove in mark_removal.items():
        if remove:
            if verbose:
                print(f"skipping existing file: {node} ({get_node_id(node)})")
            dask_graph.pop(node, None)
