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