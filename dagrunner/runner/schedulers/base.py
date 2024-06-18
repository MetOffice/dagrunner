# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
# # Abstract base class for schedulers
# from typing import Protocol, Any

# class SchedulerProtocol(Protocol):
#     _num_workers: int
#     _profiler_output: str
#     _kwargs: dict

#     def __enter__(self) -> Any:
#         NotImplementedError

#     def __exit__(self) -> None:
#         NotImplementedError

#     def run(self, dask_graph: Any, verbose: bool = False) -> None:
#         NotImplementedError
