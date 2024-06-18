"""
Standardised UI for dask compatible schedulers (including 'dask on ray')

All have in common that they convert the provided workflow dictionary into a
dask graph by initiating a dask Delayed container on each node and then
executing it (by calling its compute method) using the specified scheduler.
See the following useful background reading:

    - https://docs.dask.org/en/latest/scheduler-overview.html
    - https://docs.dask.org/en/latest/scheduling.html
    - https://docs.dask.org/en/latest/delayed.html

"""

import warnings

from dask.base import tokenize
from dask.core import get_deps
from dask.delayed import Delayed
from dask.distributed import (
    Client,
    LocalCluster,
)


def no_op(*args, **kwargs):
    """
    Dummy operation for our dask graph See [add_dummy_tasks](#function-add_dummy_tasks)

    """
    pass


def add_dummy_tasks(dask_graph):
    """
    Add a terminating dummy task to the graph as well as to each of our
    disconnected branches.

    A terminating dummy node is added to our graph to allow us to run the
    complete graph in one call as well as discard the return.
    Dummy nodes (as denoted by 'waiter' prefix in their name) are also added
    to the termination of each independent branch, as a single terminal task
    on the graph would gather all data (as its input) on the single worker and
    potentially blow past its limits. That is, one dummy task per output
    effectively ensures that no data leaves the worker.

    Args:
    - dask_graph (dict): Dask graph dict

    Returns:
    - dict: Dask graph

    TODO:
    - Potentially skip intermediate dummy for tasks with no return value.
    """
    pred_deps, succ_deps = get_deps(dask_graph)
    # Determine termination nodes for each branch
    # tokenize is used to define a deterministically unique name
    no_op_tasks = {
        "waiter-" + tokenize(dask_graph[t]): (no_op, t)
        for t, successors in succ_deps.items()
        if not successors
    }
    # Check we have no self references
    for key, value in succ_deps.items():
        if key in value:
            raise ValueError(f"Self referencing dependency: '{key}'")
    dask_graph.update(no_op_tasks)
    # Add graph termination node (if we need it)
    if len(no_op_tasks) == 1:
        (target,) = no_op_tasks.keys()
    else:
        # collect all wait keys (force computation of every task waited on)
        task = (no_op, *no_op_tasks)
        target = "waiter-" + tokenize(task)
        dask_graph[target] = task
    return dask_graph, target


class Distributed:
    """A class to run dask graphs on a distributed cluster."""

    def __init__(self, num_workers, profiler_filepath=None, **kwargs):
        self._num_workers = num_workers
        self._profiler_output = profiler_filepath
        self._kwargs = kwargs
        self._cluster = None

    def __enter__(self):
        """Create a local cluster and connect a client to it."""
        self._cluster = LocalCluster(
            n_workers=self._num_workers,
            processes=True,
            threads_per_worker=1,
            **self._kwargs,
        )
        Client(self._cluster)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._cluster.close()
        self._cluster = None

    def run(self, dask_graph, verbose=False):
        """
        Execute the provided graph.

        Args:
        - dask_graph (dict): Dask graph dictionary

        Keyword Args:
        - verbose (bool): Print out statements indicating progress.

        Returns:
        - Any: The output of the graph execution.
        """
        graph, target = add_dummy_tasks(dask_graph.copy())
        dask_container = Delayed(target, graph)
        if self._profiler_output:
            from dask.distributed import performance_report

            with performance_report(filename=self._profiler_output):
                res = dask_container.compute()
        else:
            res = dask_container.compute()
        return res


class SingleMachine:
    """A class to run dask graphs on a single machine."""

    def __init__(
        self, num_workers, scheduler="processes", profiler_filepath=None, **kwargs
    ):
        num_workers = 1 if scheduler == "single-threaded" else num_workers
        self._num_workers = num_workers
        self._profiler_output = profiler_filepath
        self._kwargs = kwargs
        self._scheduler = scheduler

    def __enter__(self):
        return self

    def run(self, dask_graph, verbose=False):
        """
        Execute the provided graph.

        Args:
        - dask_graph (dict): Dask graph dictionary

        Keyword Args:
        - verbose (bool): Print out statements indicating progress.

        Returns:
        - Any: The output of the graph execution.
        """
        graph, target = add_dummy_tasks(dask_graph.copy())
        self._dask_container = Delayed(target, graph)

        # Note the if we use the dask 'processes' scheduler, then we
        # must make use of the chunksize=1 parameter
        # See
        # https://github.com/PrefectHQ/prefect/issues/4537#issuecomment-852230766
        # for further details.  Failing to set this parameter will adversely affect
        # parallel running with multiprocessing.
        if self._profiler_output:
            from dask.diagnostics import (
                CacheProfiler,
                Profiler,
                ResourceProfiler,
                visualize,
            )

            with Profiler() as prof, ResourceProfiler(
                dt=1
            ) as rprof, CacheProfiler() as cprof:
                res = self._dask_container.compute(
                    scheduler=self._scheduler,
                    num_workers=self._num_workers,
                    chunksize=1,
                )
                visualize(
                    [prof, rprof, cprof],
                    file_path=self._profiler_output,
                    show=False,
                    save=True,
                )
            if verbose:
                print(f"{max([res.mem for res in rprof.results])}MB total memory used")
        else:
            res = self._dask_container.compute(
                scheduler=self._scheduler, num_workers=self._num_workers, chunksize=1
            )
        return res

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


class DaskOnRay:
    """A class to run dask graphs using the 'dak-on-ray' scheduler."""

    def __init__(self, num_workers, profiler_filepath=None, **kwargs):
        self._num_workers = num_workers
        self._profiler_output = profiler_filepath
        self._kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        import ray

        ray.shutdown()

    def run(self, dask_graph, verbose=False):
        """
        Execute the provided graph.

        Args:
        - dask_graph (dict): Dask graph dictionary

        Keyword Args:
        - verbose (bool): Print out statements indicating progress.

        Returns:
        - Any: The output of the graph execution.
        """
        import ray
        from ray.util.dask import ray_dask_get

        graph, target = add_dummy_tasks(dask_graph)
        dask_container = Delayed(target, graph)
        if self._profiler_output:
            warnings.warn("profiler output not supported for Ray scheduler")
        ray.init(num_cpus=self._num_workers, include_dashboard=False)
        return dask_container.compute(scheduler=ray_dask_get)
