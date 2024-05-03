# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from multiprocessing import Pool
from time import sleep
import warnings

from dask.core import get_deps


class AsyncMP:
    """
    Basic asynchronous scheduler using python built-in multiprocessing.

    Context manager for creating a pool of workers, submits jobs based on the
    condition of their dependencies completing, then finally tidies up after
    itself.

    """

    def __init__(self, nprocesses, *args, fail_fast=True, profiler_filepath=None, **kwargs):
        """
        Initialise our asynchronous multiprocessing scheduler, ready to be used.

        Args:
        - nprocesses (int):
          Number of processes to use.
        - *args:
          Positional arguments to be passed to the multiprocessing pool call.

        Keyword Args:
        - fail_fast (bool):
          When a job is found to raise an exception, stop submiting new jobs
          to the queue.  If fail_fast is True, terminate all currently running
          jobs.  If False, wait for already queued jobs to complete.
        - **kwargs:
          Keyword arguments to be passed to the multiprocessing pool call.

        """
        self._nprocesses = nprocesses
        self._args = args
        self._profiler_output = profiler_filepath
        self._kwargs = kwargs
        self._pool = None
        self._fail_fast = fail_fast
        self._failures_found = False

    def run(self, graph, verbose=False, poll_frequency=0.5):
        """
        Run the provided graph using multiprocessing.

        Args:
        - graph (dict):
          Dictionary, mapping targets to an iterable of commands.

        Keyword Args:
        - verbose (bool):
          Print out statements indicating progress.
        - poll_frequency (float):
          This is the frequency in seconds which we poll running processes.
          Dependent nodes are run if their predecessors are completed,
          as verified by this polling of status.
        """
        if self._profiler_output:
            warnings.warn('profiler output not supported for multiprocessing scheduler')

        pred_deps, succ_deps = get_deps(graph)
        completed = {target: False for target in pred_deps.keys()}

        # Submit initial nodes
        starting_nodes = []
        for tgt, deps in pred_deps.items():
            if not deps:
                starting_nodes.append(tgt)
        async_results = {}  # record of async results (running nodes)
        for node in starting_nodes:
            if verbose:
                print(f"Executing: {node}")
            async_results[node] = self._pool.apply_async(
                graph[node][0], args=graph[node][1:]
            )

        node_queue = []  # queue of targets we want to run
        while len(pred_deps) != 0:
            # Check if currently running tasks have completed
            completed = []
            for target, async_res in async_results.items():
                if async_res.ready():
                    if not async_res.successful():
                        try:
                            async_res.get()  # remote traceback
                        except Exception as err:
                            self._failures_found = True
                            command = " ".join(graph[target][2:])
                            raise RuntimeError(
                                f"Command failure, key: '{target}'\ncommand:{command}"
                            ) from err
                    pred_deps.pop(target)
                    completed.append(target)
                    node_queue.extend(succ_deps[target])  # nodes we want to run next
            [async_results.pop(target) for target in completed]  # update async results

            # Run any targets in our 'queue', then update this 'queue'
            running_nodes = []
            for target in node_queue:
                if target in async_results:
                    # Already running.
                    running_nodes.append(target)
                else:
                    if any([pred in pred_deps for pred in pred_deps[target]]):
                        # One or more predecessor hasn't run/isn't finished.
                        continue
                    else:
                        # Run this target and ensure node_queue is updated.
                        running_nodes.append(target)
                        if verbose:
                            print(f"Executing: {target}")
                        async_results[target] = self._pool.apply_async(
                            graph[target][0], args=graph[target][1:]
                        )
            if running_nodes:
                node_queue = list(
                    set(node_queue) - set(running_nodes)
                )  # update node queue

            sleep(poll_frequency)
        if node_queue:
            raise RuntimeError(f"The following targets were not executed: {node_queue}")
        if async_results:
            raise RuntimeError(
                f"The following targets did not complete execution: {async_results}"
            )

    def __enter__(self):
        """Initiate the pool of workers."""
        self._pool = Pool(self._nprocesses, *self._args, **self._kwargs)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Prevents any more tasks from being submitted to the pool.
        Once all the tasks have been completed the worker processes will
        exit.
        """
        if self._fail_fast and self._failures_found:
            self._pool.terminate()
        self._pool.close()
        # Wait for the worker processes to exit.
        self._pool.join()
