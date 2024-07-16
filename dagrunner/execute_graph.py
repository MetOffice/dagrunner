#!/usr/bin/env python3
# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import importlib
import inspect
import logging
import warnings
from functools import partial

import dask
import networkx as nx
from dask.base import tokenize
from dask.utils import apply

from dagrunner.plugin_framework import NodeAwarePlugin
from dagrunner.runner.schedulers import SCHEDULERS
from dagrunner.utils import (
    CaptureProcMemory,
    TimeIt,
    function_to_argparse,
    logger,
)
from dagrunner.utils.visualisation import visualise_graph


class _SKIP_EVENT:
    """
    This object is used to indicate to `plugin_executor` to skip execution of its node.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_SKIP_EVENT, cls).__new__(cls)
        return cls._instance

    def __repr__(self):
        return "SKIP_EVENT"

    def __hash__(self):
        return hash("SKIP_EVENT")

    def __reduce__(self):
        return (self.__class__, ())


SKIP_EVENT = _SKIP_EVENT()


class SkipBranch(Exception):
    """
    This exception is used to skip a branch of the execution graph.

    To be used in combination to one of the multiprocessing dask schedulers.
    In the single-threaded scheduler, Dask executes tasks sequentially, and
    exceptions will propagate as they occur, potentially halting the execution of
    subsequent tasks.

    ## Warning

    Status: experimental.

    """

    pass


def _get_common_args_matching_signature(callable_obj, common_kwargs, keys=None):
    """
    Get subset of arguments which match the callable signature.

    Also additionally include those 'keys' provided
    """
    keys = [] if keys is None else keys
    return {
        key: value
        for key, value in common_kwargs.items()
        if key in inspect.signature(callable_obj).parameters or key in keys
    }


def plugin_executor(
    *args,
    call=None,
    verbose=False,
    dry_run=False,
    common_kwargs=None,
    **node_properties,
):
    """
    Executes a plugin callable with the provided arguments and keyword arguments.

    Plugins can be functions or classes.  If a class, it is instantiated with the
    keyword arguments provided in the `call` tuple.  The plugin callable is then
    executed with the positional arguments provided in `args` and the keyword arguments
    provided in the `call` tuple.  A plugin call is skipped if 1 or more of the `args`
    is the `SKIP_EVENT` object.

    Args:
    - `*args`: Positional arguments to be passed to the plugin callable.
    - `call`: A tuple containing the callable object or python dot path to one, keyword
      arguments to instantiate this class (optional and where this callable is a class)
      and finally the keyword arguments to be passed to this callable.
    - `verbose`: A boolean indicating whether to print verbose output.
    - `dry_run`: A boolean indicating whether to perform a dry run without executing
      the plugin.
    - `common_kwargs`: A dictionary of optional keyword arguments to apply to all
      applicable plugins.  That is, being passed to the plugin initialisation and or
      call if such keywords are expected from the plugin.  This is a useful alternative
      to global or environment variable usage.
    - `**node_properties`: Node properties.  These will be passed to 'node-aware'
      plugins.

    Returns:
    - The result of executing the plugin function or method.

    Raises:
    - ValueError: If the `call` argument is not provided.
    """
    logger.client_attach_socket_handler()

    if common_kwargs is None:
        common_kwargs = {}
    common_kwargs.update({"verbose": verbose, "dry_run": dry_run})

    args = [
        arg for arg in args if arg is not None
    ]  # support plugins that have no return value
    if call is None:
        raise ValueError("call is a required argument")
    if verbose:
        print(f"args: {args}")
        print(f"call: {call}")
    if SKIP_EVENT in args:
        if verbose:
            print(f"Skipping node {call[0]}")
        return SKIP_EVENT

    # Handle call tuple unpacking (length 2, no class init kwargs
    # or length 3 with class init kwargs).
    try:
        callable_obj, callable_kwargs_init, callable_kwargs = call
    except ValueError as e:
        if (
            str(e) == "not enough values to unpack (expected 3, got 2)"
        ):  # no class init kwargs
            callable_obj, callable_kwargs = call
            callable_kwargs_init = {}
        else:
            raise e

    if isinstance(callable_obj, str):
        # import callable if a string is provided
        module_name, function_name = callable_obj.rsplit(".", 1)
        module = importlib.import_module(module_name)
        if verbose:
            print(f"imported module '{module}', callable '{function_name}'")
        callable_obj = getattr(module, function_name)

    call_msg = ""
    obj_name = callable_obj.__name__
    if isinstance(callable_obj, type):
        if issubclass(callable_obj, NodeAwarePlugin):
            callable_kwargs["node_properties"] = node_properties
        callable_kwargs_init = (
            callable_kwargs_init
            | _get_common_args_matching_signature(callable_obj, common_kwargs)
        )
        callable_obj = callable_obj(**callable_kwargs_init)
        call_msg = f"(**{callable_kwargs_init})"

    callable_kwargs = callable_kwargs | _get_common_args_matching_signature(
        callable_obj, common_kwargs, callable_kwargs.keys()
    )  # based on overriding arguments

    msg = f"{obj_name}{call_msg}(*{args}, **{callable_kwargs})"
    if verbose:
        print(msg)
    res = None
    if not dry_run:
        with TimeIt() as timer, dask.config.set(
            scheduler="single-threaded"
        ), CaptureProcMemory() as mem:
            res = callable_obj(*args, **callable_kwargs)
        msg = f"{str(timer)}; {msg}; {mem.max()}"
    logging.info(msg)

    if verbose:
        print(f"result: {res}")
    return res


def _attempt_visualise_graph(graph, graph_output):
    """Visualise graph but if fails, turn into a warning."""
    try:
        visualise_graph(graph, graph_output)
    except Exception as err:
        warnings.warn(f"{err}. Skipping execution graph visualisation.")


def _process_nodes(node):
    """Filter missing attributes and copy properties over as attributes."""
    return {k: v for k, v in vars(node).items() if v is not None}


def _get_networkx(networkx_graph):
    """
    Converts the input `networkx_graph` into a NetworkX DiGraph object.

    Args:
        networkx_graph (networkx.DiGraph, callable or str):
            A networkx graph; dot path to a networkx graph or callable that returns
            one (str); tuple representing (edges, nodes) or callable object that
            returns a networkx.

    Returns:
        nxgraph (networkx.DiGraph): The NetworkX DiGraph object.

    Raises:
        ValueError: If the `networkx_graph` parameter is not recognized.

    """
    if isinstance(networkx_graph, nx.DiGraph) or callable(networkx_graph):
        return networkx_graph
    elif isinstance(networkx_graph, str):
        parts = networkx_graph.split(".")
        module = importlib.import_module(".".join(parts[:-1]))
        networkx_graph = parts[-1]
        nxgraph = getattr(module, networkx_graph)
    elif callable(networkx_graph):
        nxgraph = networkx_graph()
    else:
        try:
            edges, nodes = networkx_graph
            nodes = {k: nodes[k] | _process_nodes(k) for k in nodes.keys()}.items()
            nxgraph = nx.DiGraph()
            nxgraph.add_edges_from(edges)
            nxgraph.add_nodes_from(nodes)
        except ValueError:
            raise ValueError(
                "Not recognised 'networkx_graph' parameter, see ExecuteGraph docstring."
            )
    return nxgraph


class ExecuteGraph:
    def __init__(
        self,
        networkx_graph: str,
        networkx_graph_kwargs: dict = None,
        plugin_executor: callable = plugin_executor,
        scheduler: str = "processes",
        num_workers: int = 1,
        profiler_filepath: str = None,
        dry_run: bool = False,
        verbose: bool = False,
        sqlite_filepath: str = None,
        **kwargs,
    ):
        """
        Execute a networkx graph using a chosen scheduler.

        Args:
        - `networkx_graph` (networkx.DiGraph, callable or str):
          A networkx graph; dot path to a networkx graph or callable that returns
          one; tuple representing (edges, nodes) or callable object that
          returns a networkx.
        - `networkx_graph_kwargs` (dict):
          Keyword arguments to pass to the networkx graph callable.  Optional.
        - `plugin_executor` (callable):
          A callable object that executes a plugin function or method with the provided
          arguments and keyword arguments.  By default, uses the `plugin_executor`
          function.  Optional.
        - `scheduler` (str):
          Accepted values include "ray", "multiprocessing" and those recognised
          by dask: "threads", "processes" and "single-threaded" (useful for debugging).
          See https://docs.dask.org/en/latest/scheduling.html.  Optional.
        - `num_workers` (int):
          Number of processes or threads to use.  Optional.
        - `dry_run` (bool):
          Print executed commands but don't actually run them.  Optional.
        - `profiler_filepath` (str):
          Output html profile filepath if supported by the chosen scheduler.
          See https://docs.dask.org/en/latest/diagnostics-local.html
          Optional.
        - `verbose` (bool):
          Print executed commands.  Optional.
        - `sqlite_filepath` (str):
          Filepath to a SQLite database to store log records.  Optional.
        - `**kwargs`:
          Optional global keyword arguments to apply to all applicable plugins.
        """
        self._nxgraph = _get_networkx(networkx_graph)
        self._nxgraph_kwargs = networkx_graph_kwargs or {}
        self._plugin_executor = plugin_executor
        if scheduler not in SCHEDULERS:
            raise ValueError(
                f"scheduler '{scheduler}' not recognised, please choose from "
                f"{list(SCHEDULERS.keys())}"
            )
        self._scheduler = SCHEDULERS[scheduler]
        self._num_workers = num_workers
        self._profiler_output = profiler_filepath
        self._kwargs = kwargs | {"verbose": verbose, "dry_run": dry_run}
        self._exec_graph = self._process_graph()
        self._sqlite_filepath = sqlite_filepath

    @property
    def nxgraph(self):
        return self._nxgraph

    def _process_graph(self):
        """
        Create flattened dictionary describing the relationship between nodes.

        Here we wrap our nodes to ensure common parameters are share across all
        executed nodes (e.g. dry-run, verbose).

        TODO: Potentially support 'clobber' i.e. partial graph execution from a graph
          failure recovery.
        """
        executor = partial(
            self._plugin_executor,
            verbose=self._kwargs.pop("verbose"),
            dry_run=self._kwargs.pop("dry_run"),
            common_kwargs=self._kwargs,
        )

        if callable(self._nxgraph):
            self._nxgraph = self._nxgraph(**self._nxgraph_kwargs)

        exec_graph = {}
        for node_id, properties in self._nxgraph.nodes(data=True):
            # don't use nodes in our graph as some schedulers (dask
            # distributed as per dask.core.validate_key) support only a subset
            # of types (tuples, bytes, int, float and str).
            key = tokenize(node_id)
            args = [tokenize(arg) for arg in self._nxgraph.predecessors(node_id)]
            exec_graph[key] = (apply, executor, args, properties)

        # handle_clobber(graph, workflow, no_clobber, verbose)
        return exec_graph

    def visualise(self, output_filepath: str):
        _attempt_visualise_graph(self._exec_graph, output_filepath)

    def __call__(self):
        with logger.ServerContext(sqlite_filepath=self._sqlite_filepath), TimeIt(
            verbose=True
        ), self._scheduler(
            self._num_workers, profiler_filepath=self._profiler_output
        ) as scheduler:
            try:
                res = scheduler.run(self._exec_graph)
            except SkipBranch:
                pass
        return res


def main():
    """
    Entry point of the program.
    Parses command line arguments and executes the graph using the ExecuteGraph class.
    """
    parser = function_to_argparse(ExecuteGraph, exclude=["plugin_executor"])
    args = parser.parse_args()
    args = vars(args)
    # positional arguments with '-' aren't converted to '_' by argparse.
    args = {key.replace("-", "_"): value for key, value in args.items()}
    if args.get("verbose", False):
        print(f"CLI call arguments: {args}")
    kwargs = args.pop("kwargs", None) or {}
    ExecuteGraph(**args, **kwargs)()


if __name__ == "__main__":
    main()
