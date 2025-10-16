#!/usr/bin/env python3
# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import importlib
import inspect
import logging
from functools import partial

import dask
import networkx as nx
from dask.base import tokenize
from dask.utils import apply

from dagrunner.config import CONFIG
from dagrunner.plugin_framework import IGNORE_EVENT, SKIP_EVENT, NodeAwarePlugin
from dagrunner.runner.schedulers import SCHEDULERS
from dagrunner.utils import (
    CaptureProcMemory,
    TimeIt,
    as_iterable,
    function_to_argparse_parse_args,
    logger,
)
from dagrunner.utils.networkx import visualise_graph


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
    node_id=None,
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
    - `call`: A tuple containing the callable object (plugin) or python dot path to one
      and optionally keyword arguments on instantiating and calling to that plugin:
      - `(CallableClass, kwargs_init, kwargs_call)` -> `CallableClass(**kwargs_init)(*args, **kwargs_call)`
      - `(CallableClass, {}, kwargs_call)` -> `CallableClass()(*args, **kwargs_call)`
      - `(CallableClass)` - `CallableClass()(*args)`
      - `(callable, kwargs)` -> `callable(*args, **kwargs)`
      - `(callable)` -> `callable(*args)`
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
    """  # noqa: E501
    if CONFIG["dagrunner_logging"].pop("enabled", False) is True:
        logger.client_attach_socket_handler(CONFIG["dagrunner_logging"])

    if common_kwargs is None:
        common_kwargs = {}
    common_kwargs.update({"verbose": verbose, "dry_run": dry_run})

    # support plugins that have no return value
    args = list(filter(lambda x: x is not None, args))
    if call is None:
        raise ValueError(
            f"call is a required argument\nnode_properties: {node_properties}"
        )
    if verbose:
        print(f"args: {args}")
        print(f"call: {call}")

    call = as_iterable(call)

    # IGNORE_EVENT event handling
    if len(args) > 1 and all((map(lambda x: x is IGNORE_EVENT, args))):
        # all args are IGNORE_EVENT, return IGNORE_EVENT (pass along)
        if verbose:
            print(f"Retuning 'IGNORE_EVENT' event {call[0]}")
        return IGNORE_EVENT
    args = list(filter(lambda x: x is not IGNORE_EVENT, args))

    # ignore execution if any SKIP_EVENT in args (pass along).
    if SKIP_EVENT in args:
        if verbose:
            print(f"Returning 'SKIP_EVENT' event {call[0]}")
        return SKIP_EVENT

    callable_obj = call[0]
    if isinstance(callable_obj, str):
        # import callable if a string is provided
        module_name, function_name = callable_obj.rsplit(".", 1)
        module = importlib.import_module(module_name)
        if verbose:
            print(f"imported module '{module}', callable '{function_name}'")
        callable_obj = getattr(module, function_name)

    # Handle call tuple unpacking (length 2, no class init kwargs
    # or length 3 with class init kwargs).
    if isinstance(callable_obj, type):
        if len(call) == 3:
            _, callable_kwargs_init, callable_kwargs = call
        elif len(call) == 2:
            _, callable_kwargs_init = call
            callable_kwargs = {}
        elif len(call) == 1:
            callable_kwargs = {}
            callable_kwargs_init = {}
        else:
            raise ValueError(
                f"expecting 1, 2 or 3 values to unpack for {callable_obj}, "
                f"got {len(call)}\nnode_properties: {node_properties}"
            )
        callable_kwargs_init = (
            {} if callable_kwargs_init is None else callable_kwargs_init
        )
    else:
        if len(call) == 2:
            _, callable_kwargs = call
        elif len(call) == 1:
            callable_kwargs = {}
        else:
            raise ValueError(
                f"expecting 1 or 2 values to unpack for {callable_obj}, got "
                f"{len(call)}\nnode_properties: {node_properties}"
            )
    callable_kwargs = {} if callable_kwargs is None else callable_kwargs

    call_msg = ""
    try:
        obj_name = callable_obj.__name__
    except AttributeError:
        obj_name = type(callable_obj).__name__

    if isinstance(callable_obj, type):
        if issubclass(callable_obj, NodeAwarePlugin):
            callable_kwargs["node_properties"] = node_properties
        callable_kwargs_init = (
            callable_kwargs_init
            | _get_common_args_matching_signature(callable_obj, common_kwargs)
        )
        try:
            callable_obj = callable_obj(**callable_kwargs_init)
        except Exception as err:
            msg = (
                f"Failed to initialise {obj_name} with {callable_kwargs_init}"
                f"\nnode_properties: {node_properties}"
            )
            raise RuntimeError(msg) from err
        call_msg = f"(**{callable_kwargs_init})"

    callable_kwargs = callable_kwargs | _get_common_args_matching_signature(
        callable_obj, common_kwargs, callable_kwargs.keys()
    )  # based on overriding arguments

    msg = f"{obj_name}{call_msg}(*{args}, **{callable_kwargs})"
    if verbose:
        print(msg)
    res = None
    if not dry_run:
        with (
            TimeIt() as timer,
            dask.config.set(scheduler="single-threaded"),
            CaptureProcMemory() as mem,
        ):
            try:
                res = callable_obj(*args, **callable_kwargs)
            except Exception as err:
                msg = (
                    f"Failed to execute {obj_name} with {args}, {callable_kwargs}"
                    f"\nnode_properties: {node_properties}"
                )
                raise RuntimeError(msg) from err
        msg = f"{str(timer)}; {msg}; {mem.max()}"
    logging.info(msg)

    if verbose:
        try:
            # cube looking UI
            print(f"result: {res.summary(shorten=True)}")
        except (TypeError, AttributeError):
            # fallback
            print(f"result: {res}")
    return res


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
    else:
        try:
            edges, nodes = networkx_graph
            nodes = {k: _process_nodes(k) | nodes[k] for k in nodes.keys()}.items()
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
        scheduler: str = "multiprocessing",
        num_workers: int = 1,
        profiler_filepath: str = None,
        config_filepath: str = None,
        dry_run: bool = False,
        verbose: bool = False,
        **kwargs,
    ):
        """
        Execute a networkx graph using a chosen scheduler.

        Args:
        - `networkx_graph` (networkx.DiGraph, callable or str):
          Python dot path to a `networkx.DiGraph` or tuple(edges, settings) object, or
          callable that returns one.  When called via the library, we support passing
          the `networkx.DiGraph` or `tuple(edges, settings)` objects directly.  Note
          that 'settings' represent a mapping (dictionary) between node and the node
          attributes.  When provided, DAGrunner will attempt to convert this tuple into
          a networkx through the following pseudo-code:
            1. Copy node identity properties into the node attributes dictionary
              and remove any attributes that are 'None' ('settings' from the tuple
              provided).
            2. Construct an empty networkx.DiGraph object.
            3. Add edges to this graph ('edges' from the tuple provided).
            4. Add node to attributes lookup to this graph ('settings' from the tuple
              provided).
            It is recommended that the user instead provide the networkx graph directly
            rather than relying on DAGrunner to decide how to construct it.
        - `networkx_graph_kwargs` (dict):
          Keyword arguments to pass to the `networkx_graph` when it represents a
          callable.  Optional.
        - `plugin_executor` (callable):
          A callable object that executes a plugin function or method with the provided
          arguments and keyword arguments.  By default, uses the `plugin_executor`
          function.  Optional.
        - `scheduler` (str):
          Accepted values include "ray", "multiprocessing" and those recognised
          by dask: "threads", "processes" and "single-threaded" (useful for debugging)
          and "distributed".  See https://docs.dask.org/en/latest/scheduling.html.
          Optional.
        - `num_workers` (int):
          Number of processes or threads to use.  Optional.
        - `config_filepath` (str):
          Path to the configuration file.  See [dagrunner.config](dagrunner.config.md).
          Optional.
        - `dry_run` (bool):
          Print executed commands but don't actually run them.  Optional.
        - `profiler_filepath` (str):
          Output html profile filepath if supported by the chosen scheduler.
          See https://docs.dask.org/en/latest/diagnostics-local.html
          Optional.
        - `verbose` (bool):
          Print executed commands.  Optional.
        - `**kwargs`:
          Optional global keyword arguments to apply to all applicable plugins.
        """
        if config_filepath:
            CONFIG.parse_configuration(config_filepath)

        self._nxgraph = _get_networkx(networkx_graph)
        self._nxgraph_kwargs = networkx_graph_kwargs or {}
        self._plugin_executor = plugin_executor
        if scheduler not in SCHEDULERS:
            raise ValueError(
                f"scheduler '{scheduler}' not recognised, please choose from "
                f"{list(SCHEDULERS.keys())}"
            )
        if dry_run:
            scheduler = "single-threaded"
        self._scheduler = SCHEDULERS[scheduler]
        self._num_workers = num_workers
        self._profiler_output = profiler_filepath
        self._kwargs = kwargs | {"verbose": verbose, "dry_run": dry_run}
        self._exec_graph = self._process_graph()

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

        if CONFIG["dagrunner_visualisation"].pop("enabled", False) is True:
            self.visualise(**CONFIG["dagrunner_visualisation"])

        exec_graph = {}
        for node_id, properties in self._nxgraph.nodes(data=True):
            # don't use nodes in our graph as some schedulers (dask
            # distributed as per dask.core.validate_key) support only a subset
            # of types (tuples, bytes, int, float and str).
            key = tokenize(node_id)
            args = [tokenize(arg) for arg in self._nxgraph.predecessors(node_id)]
            exec_graph[key] = (apply, executor, args, properties | {"node_id": node_id})

        # handle_clobber(graph, workflow, no_clobber, verbose)
        return exec_graph

    def visualise(self, **kwargs):
        visualise_graph(self._nxgraph, **kwargs)

    def __call__(self):
        with (
            TimeIt(verbose=True),
            self._scheduler(
                self._num_workers, profiler_filepath=self._profiler_output
            ) as scheduler,
        ):
            res = scheduler.run(self._exec_graph)
        return res


def main():
    """
    Entry point of the program.
    Parses command line arguments and executes the graph using the ExecuteGraph class.
    """
    args, kwargs = function_to_argparse_parse_args(
        ExecuteGraph, exclude=["plugin_executor"]
    )
    ExecuteGraph(**args, **kwargs)()


if __name__ == "__main__":
    main()
