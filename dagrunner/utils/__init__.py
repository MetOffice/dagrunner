# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import argparse
import dataclasses
import inspect
import itertools
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import warnings
from abc import ABC, abstractmethod
from dataclasses import fields
from glob import glob
from typing import Iterable

import dagrunner.utils._doc_styles as doc_styles


def subset_equality(obj_a, obj_b):
    """
    Return whether obj_a is a subset of obj_b.

    Supporting namedtuple and dataclasses, otherwise fallback to equality.  Note that
    a 'None' value in obj_a is considered a wildcard.
    """
    ret = True
    sametype = type(obj_a) is type(obj_b)
    if sametype and dataclasses.is_dataclass(obj_a):
        # dataclass
        for field in fields(obj_a):
            if getattr(obj_a, field.name) is not None and getattr(
                obj_a, field.name
            ) != getattr(obj_b, field.name):
                ret = False
                break
    elif sametype and hasattr(obj_a, "_fields"):
        # namedtuple
        for field in obj_a._fields:
            if getattr(obj_a, field) is not None and getattr(obj_a, field) != getattr(
                obj_b, field
            ):
                ret = False
                break
    else:
        warnings.warn(
            f"subset equality on incompatible object types '{type(obj_a)}' "
            f"with '{type(obj_b)}', falling back to equality"
        )
        ret = obj_a == obj_b
    return ret


def pairwise(iterable):
    """
    Return successive overlapping pairs taken from the input iterable.

    The number of 2-tuples in the output iterator will be one fewer than the
    number of inputs. It will be empty if the input iterable has fewer than
    two values.

    pairwise('ABCDEFG') → AB BC CD DE EF FG
    """
    if sys.version_info >= (3, 10):
        warnings.warn(
            "The 'pairwise' function is deprecated. Use 'itertools.pairwise' instead.",
            DeprecationWarning,
        )
    iterator = iter(iterable)
    a = next(iterator, None)
    for b in iterator:
        yield a, b
        a = b


def in_notebook():
    """Determine whether we are in a Jupyter notebook."""
    res = False
    try:
        from IPython import get_ipython

        res = "IPKernelApp" in get_ipython().config
    except (ImportError, AttributeError):
        pass
    return res


def as_iterable(obj):
    if obj is None:
        return []
    elif not isinstance(obj, Iterable) or isinstance(obj, (str, bytes, dict)):
        obj = [obj]
    return obj


class Singleton(type):
    """
    Singleton metaclass.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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


def data_polling(
    *args, timeout=60 * 2, polling=1, file_count=None, fail_fast=True, verbose=False
):
    """
    Poll for the availability of files

    Poll for data and return when all data is available or otherwise raise an
    exception if the timeout is reached.

    Args:
    - *args: Variable length argument list of file patterns to be checked.
        `<hostname>:<path>` syntax supported for files on a remote host.

    Args:
    - timeout (int): Timeout in seconds (default is 120 seconds).
    - polling (int): Time interval in seconds between each poll (default is 1
        second).
    - file_count (int): Expected number of files to be found for globular
        expansion (default is >= 1 files per pattern).
    - fail_fast (bool): Stop when a file is not found (default is True).
    - verbose (bool): Print verbose output.
    """

    # Define a key function
    def host_and_glob_key(path):
        psplit = path.split(":")
        host = psplit[0] if ":" in path else ""  # Extract host if available
        is_glob = psplit[-1] if "*" in psplit[-1] else ""  # Glob pattern
        return (host, is_glob)

    time_taken = 0
    fpaths_found = set()
    fpaths_not_found = set()
    args = list(map(process_path, args))

    # Group by host and whether it's a glob pattern
    sorted_args = sorted(args, key=host_and_glob_key)
    args_by_host = [
        [key, set(map(lambda path: path.split(":")[-1], group))]
        for key, group in itertools.groupby(sorted_args, key=host_and_glob_key)
    ]

    for ind, ((host, globular), paths) in enumerate(args_by_host):
        globular = bool(globular)
        host_msg = f"{host}:" if host else ""
        while True:
            if host:
                # bash equivalent to python glob (glob on remote host)
                expanded_paths = subprocess.run(
                    "ssh -o BatchMode=yes -o StrictHostKeyChecking=no "
                    f"{host} 'for file in {' '.join(paths)}; do if "
                    '[ -e "$file" ]; then echo "$file"; fi; done\'',
                    shell=True,
                    check=True,
                    text=True,
                    capture_output=True,
                ).stdout.strip()
                if expanded_paths:
                    expanded_paths = expanded_paths.split("\n")
            else:
                expanded_paths = list(itertools.chain.from_iterable(map(glob, paths)))
            if expanded_paths:
                if host:
                    fpaths_found = fpaths_found.union(
                        set([f"{host}:{path}" for path in expanded_paths])
                    )
                else:
                    fpaths_found = fpaths_found.union(expanded_paths)
                if globular and (not file_count or len(expanded_paths) >= file_count):
                    # globular expansion completed
                    paths = set()
                else:
                    # Remove paths we have found
                    paths = paths - set(expanded_paths)

            if paths:
                if timeout and time_taken < timeout:
                    if verbose:
                        print(
                            f"polling for {host_msg}{paths}, time taken: "
                            f"{time_taken}s of limit {timeout}s"
                        )
                    time.sleep(polling)
                    time_taken += polling
                else:
                    break
            else:
                break

        if paths:
            if host:
                fpaths_not_found = fpaths_not_found.union(
                    set([f"{host}:{path}" for path in paths])
                )
            else:
                fpaths_not_found = fpaths_not_found.union(paths)

            if fail_fast:
                break

    return fpaths_found, fpaths_not_found


class _RemotePathHandler:
    def __init__(self, fpath):
        self._fpath = fpath
        self._host, self._lpath = None, fpath
        if ":" in fpath:
            self._host, self._lpath = fpath.split(":")

    @property
    def host(self):
        self._host

    @property
    def local_path(self):
        self._lpath

    def __str__(self):
        return self._fpath

    def exists(self):
        if self._host:
            # check if file exists on remote host
            exists = (
                subprocess.run(
                    [
                        "ssh",
                        "-o",
                        "BatchMode=yes",
                        "-o",
                        "StrictHostKeyChecking=no",
                        self._host,
                        "test",
                        "-e",
                        self._lpath,
                    ],
                    check=False,
                ).returncode
                == 0
            )
        else:
            exists = os.path.exists(self._lpath)
        return exists

    def get_identity(self):
        """An identity derived from modification time and file size in bytes"""
        if self._host:
            mtime = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "StrictHostKeyChecking=no",
                    self._host,
                    "stat",
                    "-c",
                    "%Y_%s",
                    self._lpath,
                ],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
        else:
            mtime = (
                f"{int(os.path.getmtime(self._lpath))}_{os.path.getsize(self._lpath)}"
            )
        return mtime

    def copy(self, target):
        if self._host:
            rsync_command = ["scp", "-p", f"{self._host}:{self._lpath}", target]
            subprocess.run(rsync_command, check=True, text=True, capture_output=True)
        else:
            try:
                os.link(self._lpath, target)
            except Exception:
                warnings.warn(
                    f"Failed to hard link {self._lpath} to {target}. Copying instead."
                )
                shutil.copy2(self._lpath, target)


def stage_to_dir(*args, staging_dir, verbose=False):
    """
    Copy input filepaths to a staging area and update paths.

    Hard link copies are preferred (same host) and physical copies are made otherwise.
    File name, size and modification time are used to evaluate if the destination file
    exists already (matching criteria of rsync).  If exists already, skip the copy.
    Staged files are named: `<modification-time>_<file-size>_<filename>` to avoid
    collision with identically names files.
    """
    os.makedirs(staging_dir, exist_ok=True)
    args = list(args)
    for ind, arg in enumerate(args):
        fpath = _RemotePathHandler(arg)
        if not fpath.exists():
            raise FileNotFoundError(f"File '{fpath}' not found.")

        source_mtime_size = fpath.get_identity()

        target = os.path.join(
            staging_dir, f"{source_mtime_size}_{os.path.basename(str(fpath))}"
        )
        if not os.path.exists(target):
            if verbose:
                print(f"Staged '{arg}' to '{target}'")
            fpath.copy(target)
        else:
            warnings.warn(
                f"'{arg}' staged file '{target}' already exists. Skipping copy."
            )

        args[ind] = target
    return args
