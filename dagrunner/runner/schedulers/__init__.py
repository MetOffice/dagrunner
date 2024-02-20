# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'pp_systems_framework' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from functools import partial
from . import asyncmp
from . import dask


SCHEDULERS = {
    "distributed": dask.Distributed,
    "threads": partial(dask.SingleMachine, scheduler="threads"),
    "processes": partial(dask.SingleMachine, scheduler="processes"),
    "single-threaded": partial(dask.SingleMachine, scheduler="single-threaded"),
    "multiprocessing": asyncmp.AsyncMP,
    "ray": dask.DaskOnRay,
}
