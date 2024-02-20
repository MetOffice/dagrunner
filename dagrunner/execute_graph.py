#!/usr/bin/env python3
# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'pp_systems_framework' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import gc
import json
import os
import shutil
import tempfile
import warnings
from functools import partial

import importlib

import dask
from dask.core import get_deps
from dask.utils import apply
from dagrunner.utils import (
    ObjectAsStr,
    TimeIt,
    function_to_argparse,
)
from dagrunner.plugin_framework import NodeAwarePlugin
from dagrunner.runner.schedulers import SCHEDULERS
from dagrunner.utils.visualisation import visualise_graph


class SkipBranch(Exception):
    """
    This exception is used to skip a branch of the execution graph.
    
    To be used in combination to one of the multiprocessing schedulers.
    In the single-threaded scheduler, Dask executes tasks sequentially, and
    exceptions will propagate as they occur, potentially halting the execution of
    subsequent tasks.

    """
    pass


def plugin_executor(*args, call=None, verbose=False, dry_run=False, **kwargs):
    # args = [getattr(obj, "original_object", obj) for obj in args]
    args = [arg for arg in args if arg is not None]  # supporting plugins that have no return
    if call is None:
        raise ValueError("call is a required argument")
    if verbose:
       print(f"args: {args}")
       print(f"call: {call}")

    callable_obj, callable_kwargs = call
    if isinstance(callable_obj, str):
        # import callable if a string is provided
        module_name, function_name = callable_obj.rsplit('.', 1)
        module = importlib.import_module(module_name)
        if verbose:
            print(f"imported module '{module}', callable '{function_name}'")
        callable_obj = getattr(module, function_name)

    with dask.config.set(scheduler="single-threaded"):
        if issubclass(callable_obj, NodeAwarePlugin):
            node_properties = kwargs
            callable_kwargs["node_properties"] = node_properties
        if isinstance(callable_obj, type):
            if verbose:
                print(f"{callable_obj.__name__}(*{args}, **{callable_kwargs})")
            res = callable_obj()(*args, verbose=verbose, **callable_kwargs)
        else:
            if verbose:
                print(f"{callable_obj.__name__}()(*{args}, **{callable_kwargs})")
            res = callable_obj(*args, verbose=verbose, **callable_kwargs)

    if verbose:
        print(f"result: '{res}'")

    # if res and not isinstance(res, ObjectAsStr):
    #     # ObjectAsStr protects against circular dependencies in an executed graph
    #     res = ObjectAsStr(res, str(res))
    return res


def _attempt_visualise_graph(graph, graph_output):
    """Visualise graph but if fails, turn into a warning."""
    try:
        visualise_graph(graph, graph_output)
    except Exception as err:
        warnings.warn(f"{err}. Skipping execution graph visualisation.")


def _get_networkx(config_dot_path):
    parts = config_dot_path.split('.')
    module = importlib.import_module('.'.join(parts[:-1]))
    networkx_graph = parts[-1]
    nxgraph = getattr(module, networkx_graph)
    return nxgraph


class ExecuteGraph:
    def __init__(self, networkx_graph_dot_path: str,
                 plugin_executor: callable = plugin_executor,
                 scheduler: str = "processes",
                 num_workers: int = 1,
                 profiler_filepath: str = None,
                 dry_run: bool = False,
                 verbose: bool = False,
                 **kwargs):
        """
        Execute a networkx graph using a chosen scheduler.

        Args:
            networkx_graph_dot_path (networkx.DiGraph or str):
                A networkx graph or the dot path to a networkx configuration to execute.
            scheduler (str):
                Accepted values include "ray", "multiprocessing" and those recognised
                by dask: "threads", "processes" and "single-threaded" (useful for debugging).
                See https://docs.dask.org/en/latest/scheduling.html.  Optional.
            num_workers (int):
                Number of processes or threads to use.  Optional.
            dry_run (bool):
                Print executed commands but don't actually run them.  Optional.
            profiler_filepath (str):
                Output html profile filepath if supported by the chosen scheduler.
                See https://docs.dask.org/en/latest/diagnostics-local.html
                Optional.
            verbose (bool):
                Print executed commands.  Optional.
            **kwargs:
                Keyword arguments common to all plugin execution (applied using functools.partial).
                Typical examples include 'verbose', 'dry-run' etc.  Note that
                verbose and dry-run are common to all workflows and to have explicit arguments above.
        """
        nxgraph = _get_networkx(networkx_graph_dot_path)
        self._plugin_executor = plugin_executor
        if scheduler not in SCHEDULERS:
            raise ValueError(f"scheduler '{scheduler}' not recognised, please choose from {list(SCHEDULERS.keys())}")
        self._scheduler = SCHEDULERS[scheduler]
        self._num_workers = num_workers
        self._profiler_output = profiler_filepath
        self._kwargs = kwargs | {"verbose": verbose, "dry_run": dry_run}
        self._exec_graph = self._process_graph(nxgraph)

    def _process_graph(self, nxgraph):
        """
        Create flattened dictionary describing the relationship between each of our nodes.
        Here we wrap our nodes to ensure common parameters are share accross all
        executed nodes (e.g. dry-run, verbose).
        
        TODO: Potentially support 'clobber' i.e. partial graph execution from a graph failure recovery.
        """
        executor = partial(
            self._plugin_executor,
            **self._kwargs,
        )

        if callable(nxgraph):
            nxgraph = nxgraph()

        exec_graph = {}
        for node_id, properties in nxgraph.nodes(data=True):
            key = node_id
            quoted_key = ObjectAsStr(node_id)
            args = list(nxgraph.predecessors(node_id))
            kwargs = properties
            exec_graph[key] = (apply, executor, args, kwargs)

        #handle_clobber(graph, workflow, no_clobber, verbose)
        return exec_graph

    def visualise(self, output_filepath: str):
        _attempt_visualise_graph(self._exec_graph, output_filepath)

    def __call__(self):
        with TimeIt("execute_graph"):
            with self._scheduler(self._num_workers,
                                 profiler_filepath=self._profiler_output) as scheduler:
                try:
                    res = scheduler.run(self._exec_graph)
                except SkipBranch as err:
                    pass
        return res


if __name__ == "__main__":
    parser = function_to_argparse(ExecuteGraph, exclude=["plugin_executor", "**kwargs"])
    args = parser.parse_args()
    args = vars(args)
    # positional argument '-' aren't converted to '_' by argparse.
    args = {key.replace("-", "_"): value for key, value in args.items()}
    if args.get('verbose', False):
        print(f"CLI call arguments: {args}")
    ExecuteGraph(**args)()
