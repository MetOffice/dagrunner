# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
Supackage which provides access to various schedulers through a common UI.

A SCHEDULERS dictionary provides access to the available schedulers through a
name-scheduler lookup:
- distributed
- threads
- processes
- single-threaded
- multiprocessing
- ray
"""

from functools import partial

from . import asyncmp, dask

# Schedulers that can be used with the runner, a name-lookup.
SCHEDULERS = {
    "distributed": dask.Distributed,
    "threads": partial(dask.SingleMachine, scheduler="threads"),
    "processes": partial(dask.SingleMachine, scheduler="processes"),
    "single-threaded": partial(dask.SingleMachine, scheduler="single-threaded"),
    "multiprocessing": asyncmp.AsyncMP,
    "ray": dask.DaskOnRay,
}
