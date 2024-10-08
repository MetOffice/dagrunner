# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import argparse
import inspect
import os
import socket
import threading
import time
from abc import ABC, abstractmethod

import dagrunner.utils._doc_styles as doc_styles


def process_path(fpath: str) -> str:
    """
    Process path.

    Args:
    - `fpath`: Remote path in the format <host>:<path>.  If host corresponds to
      the local host, then the host element will be removed.

    Returns:
    - Processed path
    """
    fpath = str(fpath)
    if ":" in fpath:
        host, fpath = fpath.split(":")
        # check against short and full (+domain) hostname
        if socket.gethostname() != host and socket.gethostname().split(".")[0] != host:
            fpath = f"{host}:{fpath}"
    return fpath


def get_proc_mem_stat(pid=None):
    """
    Get process memory statistics from /proc/<pid>/status.

    More information can be found at
    https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.txt

    Args:
    - `pid`: Process id.  Optional.  Default is the current process.

    Returns:
    - Dictionary with memory statistics in MB.  Fields are VmSize, VmRSS, VmPeak and
      VmHWM.

    """
    pid = os.getpid() if pid is None else int(pid)
    status_path = f"/proc/{pid}/status"
    memory_stats = {}
    with open(status_path, "r") as file:
        for line in file:
            if line.startswith(("VmSize:", "VmRSS:", "VmPeak:", "VmHWM:")):
                key, value = line.split(":", 1)
                memory_stats[key.strip()] = (
                    float(value.split()[0].strip()) / 1024.0
                )  # convert kb to mb
    return memory_stats


class _CaptureMemory(ABC):
    """Abstract class to capture maximum memory statistics."""

    def __init__(self, interval=1.0, **kwargs):
        """
        Initialize the memory capture.

        Args:
        - `interval`: Time interval in seconds to capture memory statistics.
          Note that memory statistics are captured by reading `/proc` files.  It is
          advised not to reduce the interval too much, otherwise we increase the
          overhead of reading the files.
        """
        self._interval = interval
        self._max_memory_stats = {}
        self._stop_event = threading.Event()
        self._params = kwargs

    @property
    @abstractmethod
    def METHOD(self):
        pass

    def _capture_memory(self):
        while not self._stop_event.is_set():
            current_stats = self.METHOD(**self._params)
            if not self._max_memory_stats:
                self._max_memory_stats = {key: 0 for key in current_stats}
            for key in current_stats:
                if current_stats[key] > self._max_memory_stats[key]:
                    self._max_memory_stats[key] = current_stats[key]
            # Wait for the interval or until stop event is set
            if self._stop_event.wait(self._interval):
                break

    def __enter__(self):
        self._thread = threading.Thread(target=self._capture_memory)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._stop_event.set()
        self._thread.join()

    def max(self):
        """
        Return maximum memory statistics.

        Returns:
        - Dictionary with memory statistics in MB.
        """
        return self._max_memory_stats


class CaptureProcMemory(_CaptureMemory):
    """
    Capture maximum process memory statistics.

    See `get_proc_mem_stat` for more information.
    """

    @property
    def METHOD(self):
        return get_proc_mem_stat

    def __init__(self, interval=1.0, pid=None):
        """
        Initialize the memory capture.

        Args:
        - `interval`: Time interval in seconds to capture memory statistics.
          Note that memory statistics are captured by reading /proc files.  It is
          advised not to reduce the interval too much, otherwise we increase the
          overhead of reading the files.
        - `pid`: Process id.  Optional.  Default is the current process.

        """
        super().__init__(interval=interval, pid=pid)


def get_sys_mem_stat():
    """
    Get system memory statistics from /proc/meminfo.

    More information can be found at
    https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.txt

    Returns:
    - Dictionary with memory statistics in MB.  Fields are Committed_AS, MemFree,
      Buffers, Cached and MemTotal.

    """
    status_path = "/proc/meminfo"
    memory_stats = {}
    with open(status_path, "r") as file:
        for line in file:
            if line.startswith(
                ("Committed_AS:", "MemFree:", "Buffers:", "Cached:", "MemTotal:")
            ):
                key, value = line.split(":", 1)
                memory_stats[key.strip()] = (
                    float(value.split()[0].strip()) / 1024.0
                )  # convert kb to mb
    return memory_stats


class CaptureSysMemory(_CaptureMemory):
    """
    Capture maximum system memory statistics.

    See `get_sys_mem_stat` for more information.
    """

    @property
    def METHOD(self):
        return get_sys_mem_stat


class ObjectAsStr(str):
    """Hide object under a string."""

    __slots__ = ("original_object",)

    def __new__(cls, obj, name=None):
        if isinstance(obj, cls):
            # return object as already wrapped
            return obj
        name = cls.obj_to_name(obj, type(obj) if name is None else name)
        self = super().__new__(cls, name)
        self.original_object = obj
        return self

    def __hash__(self):
        # make sure our hash doesn't clash with normal string hash
        return super().__hash__() ^ hash(type(self))

    @staticmethod
    def obj_to_name(obj, cls):
        if isinstance(obj, str):
            return obj
        obj_id = hash(obj) if not isinstance(obj, type) else id(obj)
        return f"<{cls.__module__}.{cls.__name__}@{obj_id}>"


class TimeIt:
    """
    Timer context manager which can also be used as a standalone timer.

    We can query our timer for the elapsed time in seconds even before .

    Example as a context manager:

        >>> with TimeIt() as timer:
        >>>     sleep(0.05)
        >>> print(timer)
        "Elapsed time: 0.05s"

    Example as a standalone timer:

        >>> timer = TimeIt()
        >>> timer.start_timer()
        >>> sleep(0.05)
        >>> print(timer)
        "Elapsed time: 0.05s"

    """

    def __init__(self, verbose=False):
        self._verbose = verbose
        self._total_elapsed = 0
        self._start = None
        self._running = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
        if self._verbose:
            print(str(self))
        return False

    def start(self):
        self._running = True
        self._start = time.perf_counter()

    def stop(self):
        if not self._running:
            raise RuntimeError("Timer is not running.")
        self._total_elapsed = self.elapsed
        self._running = False

    @property
    def elapsed(self):
        """Return elapsed time in seconds."""
        if self._running:
            elapsed = self._total_elapsed + (time.perf_counter() - self._start)
        else:
            elapsed = self._total_elapsed
        return elapsed

    def __str__(self):
        """Print elapsed time in seconds."""
        return f"Elapsed time: {self.elapsed:.2f}s"


def docstring_parse(obj):
    doc = obj.__doc__
    if doc_styles.RSTStyle.is_style(doc):
        parser = doc_styles.RSTStyle(doc)
    elif doc_styles.GoogleStyle.is_style(doc):
        parser = doc_styles.GoogleStyle(doc)
    elif doc_styles.NumpyStyle.is_style(doc):
        parser = doc_styles.NumpyStyle(doc)
    else:
        parser = doc_styles.MDStyle(doc)
    desc = parser.description
    var_mapping = parser.variable_mapping if parser.is_style(doc) else {}
    if var_mapping:
        var_mapping = {k.replace("*", ""): v for k, v in var_mapping.items()}
    return desc, var_mapping


class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        key, value = values
        if not hasattr(namespace, self.dest) or getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, {})
        getattr(namespace, self.dest)[key] = value


# TODO: Support for *args
#       Check signature against docstring (inconsistency)
#       'how it works' docstring
#       more sophisticated support for classes (class.__call__ etc.)
def function_to_argparse(func, parser=None, exclude=None):
    """Generate an argparse from a function signature"""
    if exclude is None:
        exclude = []

    name = func.__name__
    is_method = False
    if isinstance(func, type):
        is_method = True
        func = func.__init__
    func_desc, arg_mapping = docstring_parse(func)
    if parser:
        parser = parser.add_parser(name.replace("_", "-"), help=func_desc)
    else:
        parser = argparse.ArgumentParser(
            description=func_desc, formatter_class=argparse.RawDescriptionHelpFormatter
        )

    sig = inspect.signature(func)
    singature_param = (
        list(sig.parameters.items())[1:] if is_method else sig.parameters.items()
    )
    for name, param in singature_param:
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            print(
                f"'function_to_argparse' parameter expansion '{param}' not "
                "supported yet"
            )
            continue
        if name in exclude:
            continue

        arg_name = name.replace("_", "-")
        arg_type = param.annotation
        arg_default = param.default if param.default is not param.empty else None
        arg_optional = (
            "optional" in arg_mapping[name].lower()
            if name in arg_mapping
            else arg_default is not None
        )
        arg_kwargs = dict(
            type=arg_type,
            default=arg_default,
            help=arg_mapping[name] if name in arg_mapping else None,
        )
        if arg_type is bool:
            arg_kwargs.update(dict(action=f"store_{str(not arg_default).lower()}"))
            arg_kwargs.pop("type")
        elif arg_type in [list, set, tuple]:
            arg_num = "*" if arg_optional else "+"
            arg_kwargs.update(dict(nargs=arg_num))
            arg_kwargs["type"] = str
        elif param.kind == inspect.Parameter.VAR_KEYWORD or arg_type is dict:
            arg_kwargs.pop("type")
            arg_kwargs["nargs"] = 2
            arg_kwargs["action"] = KeyValueAction
            arg_kwargs["metavar"] = ("key", "value")
            arg_kwargs["help"] += "\n Key-value pair argument."
            arg_optional = (
                True if param.kind == inspect.Parameter.VAR_KEYWORD else arg_optional
            )

        if (
            param.default is not param.empty
            or param.kind == inspect.Parameter.VAR_KEYWORD
            or arg_type is dict
        ):
            # is a keywarg
            arg_kwargs["dest"] = name
            arg_kwargs["required"] = not arg_optional
            arg_name = f"--{arg_name}"
        arg_args = [arg_name]
        parser.add_argument(*arg_args, **arg_kwargs)

    return parser


def function_to_argparse_parse_args(*args, **kwargs):
    parser = function_to_argparse(*args, **kwargs)
    args = parser.parse_args()
    args = vars(args)
    # positional arguments with '-' aren't converted to '_' by argparse.
    args = {key.replace("-", "_"): value for key, value in args.items()}
    if args.get("verbose", False):
        print(f"CLI call arguments: {args}")
    kwargs = args.pop("kwargs", None) or {}
    return args, kwargs
