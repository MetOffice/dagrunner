# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import itertools
import json
import os
import pickle
import shutil
import string
import subprocess
import time
import warnings
from abc import ABC, abstractmethod
from glob import glob

from dagrunner.utils import process_path, Singleton


class _EventBase:
    def __repr__(self):
        # Ensures easy identification when printing/logging.
        return self.__class__.__name__.upper()

    def __hash__(self):
        # Ensures that can be used as keys in dictionaries or stored as sets.
        return hash(self.__class__.__name__.upper())

    def __reduce__(self):
        # Ensures that can be serialised and deserialised using pickle.
        return (self.__class__, ())


class _SkipEvent(_EventBase, metaclass=Singleton):
    """
    A plugin that returns a 'SKIP_EVENT' will cause `plugin_executor` to skip execution
    of all descendant node execution.
    """

    pass


SKIP_EVENT = _SkipEvent()


class _IgnoreEvent(_EventBase, metaclass=Singleton):
    """
    A plugin that returns an 'IGNORE_EVENT' will be filtered out as arguments by
    `plugin_executor` in descendant node execution.
    """

    pass


IGNORE_EVENT = _IgnoreEvent()


class Plugin(ABC):
    """Abstract base class to define our plugin UI"""

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        The main method of the plugin (abstract method).

        Positional arguments represent the plugin's inputs (dependencies),
        while keyword arguments represent the plugin's parameters.

        Args:
        - *args: Positional arguments.
        - **kwargs: Keyword arguments.

        Returns:
        - Any: The output of the plugin.

        """
        raise NotImplementedError


class NodeAwarePlugin(Plugin):
    """
    An abstract base class plugin that is of type that instructs the plugin
    executor to pass it node parameters.  This enables the definition of plugins
    that are 'node aware'.
    """


class Shell(Plugin):
    def __call__(self, *args, **kwargs):
        """
        Execute a subprocess command.

        Args:
        - *args: The command to be executed.
        - **kwargs: Additional keyword arguments to be passed to `subprocess.run`

        Returns:
        - CompletedProcess: An object representing the completed process.

        Raises:
        - CalledProcessError: If the command returns a non-zero exit status.
        """
        return subprocess.run(*args, **kwargs, shell=True, check=True)


def _stage_to_dir(*args, staging_dir, verbose=False):
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
        host, fpath = None, arg
        if ":" in arg:
            host, fpath = arg.split(":")

        if host:
            source_mtime_size = subprocess.run(
                ["ssh", host, "stat", "-c", "%Y_%s", fpath],
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
        else:
            source_mtime_size = (
                f"{int(os.path.getmtime(fpath))}_{os.path.getsize(fpath)}"
            )

        target = os.path.join(
            staging_dir, f"{source_mtime_size}_{os.path.basename(fpath)}"
        )
        if not os.path.exists(target):
            if host:
                rsync_command = ["scp", "-p", f"{host}:{fpath}", target]
                subprocess.run(
                    rsync_command, check=True, text=True, capture_output=True
                )
            else:
                try:
                    os.link(arg, target)
                except Exception:
                    warnings.warn(
                        f"Failed to hard link {arg} to {target}. Copying instead."
                    )
                    shutil.copy2(arg, target)
        else:
            warnings.warn(f"Staged file {target} already exists. Skipping copy.")

        args[ind] = target
        if verbose:
            print(f"Staged {arg} to {args[ind]}")
    return args


class Load(Plugin):
    @abstractmethod
    def load(self, *args, **kwargs):
        """
        Load data from a file.

        Args:
        - *args: Positional arguments.
        - **kwargs: Keyword arguments.

        Returns:
        - Any: The loaded data.

        Raises:
        - NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def __call__(self, *args, staging_dir=None, verbose=False, **kwargs):
        """
        Load data from a file or list of files.

        Args:
        - *args: List of filepaths to load. `<hostname>:<path>` syntax supported
          for loading files from a remote host.
        - staging_dir: Directory to stage files in.  If the staging directory doesn't
          exist, then create it.
        - verbose: Print verbose output.
        """
        args = list(map(process_path, args))
        if (
            any([arg.split(":")[0] for arg in args if ":" in arg])
            and staging_dir is None
        ):
            raise ValueError(
                "Staging directory must be specified for loading remote files."
            )

        if staging_dir and args:
            args = _stage_to_dir(*args, staging_dir=staging_dir, verbose=verbose)

        return self.load(*args, **kwargs)


class DataPolling(Plugin):
    def __init__(self, timeout=60 * 2, polling=1, file_count=None, error_on_missing=True, return_found=False, verbose=False):
        """
        Args:
        - timeout (int): Timeout in seconds (default is 120 seconds).
        - polling (int): Time interval in seconds between each poll (default is 1
          second).
        - file_count (int): Expected number of files to be found for globular
            expansion (default is >= 1 files per pattern).
        - error_on_missing (bool): Raise an exception if files are missing.
        - return_found (bool): Return list of files found if True, otherwise return
          None.  error_on_missing and return_found cannot both be False.
          When False, the DataPolling plugin acts only to indicate successful
          completion of the poll, thereby triggering the execution of steps dependent
          on this poll.
          wile setting to True will mean that the plugin additionally passes along
          files it has found.
        - verbose (bool): Print verbose output.
        """
        self._timeout = timeout
        self._polling = polling
        self._file_count = file_count
        self._error_on_missing = error_on_missing
        self._return_found = return_found
        self._verbose = verbose

        if not error_on_missing and not return_found:
            raise ValueError(
                "error_on_missing and return_found cannot both be False"
            )

    def __call__(self, *args):
        """
        Poll for the availability of files

        Poll for data and return when all data is available or otherwise raise an
        exception if the timeout is reached.

        Args:
        - *args: Variable length argument list of file patterns to be checked.
          `<hostname>:<path>` syntax supported for files on a remote host.

        Returns:
        - None, SKIP_EVENT or set:
          Returning 'None' where 'return_found' is False, returning 'SKIP_EVENT' if
          'error_on_missing' is True and returning a 'set' of files found if
          'return_found' is True.

        Raises:
        - RuntimeError: If the timeout is reached before all files are found.
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
                        f'ssh {host} \'for file in {" ".join(paths)}; do if '
                        '[ -e "$file" ]; then echo "$file"; fi; done\'',
                        shell=True,
                        check=True,
                        text=True,
                        capture_output=True,
                    ).stdout.strip()
                    if expanded_paths:
                        expanded_paths = expanded_paths.split("\n")
                else:
                    expanded_paths = list(
                        itertools.chain.from_iterable(map(glob, paths))
                    )
                if expanded_paths:
                    if host:
                        fpaths_found = fpaths_found.union(set([f"{host}:{path}" for path in expanded_paths]))
                    else:
                        fpaths_found = fpaths_found.union(expanded_paths)
                    if globular and (
                        not self._file_count or len(expanded_paths) >= self._file_count
                    ):
                        # globular expansion completed
                        paths = set()
                    else:
                        # Remove paths we have found
                        paths = paths - set(expanded_paths)

                if paths:
                    if self._timeout and time_taken < self._timeout:
                        print(
                            f"self._polling for {host_msg}{paths}, time taken: "
                            f"{time_taken}s of limit {self._timeout}s"
                        )
                        time.sleep(self._polling)
                        time_taken += self._polling
                    else:
                        break
                else:
                    break

            if paths:
                if host:
                    fpaths_not_found = fpaths_not_found.union(set([f"{host}:{path}" for path in paths]))
                else:
                    fpaths_not_found = fpaths_not_found.union(paths)
                if self._error_on_missing:
                    raise FileNotFoundError(
                        f"Timeout waiting for: {host_msg}{'; '.join(sorted(paths))}"
                    )
                elif not self._return_found:
                    return SKIP_EVENT

        if self._verbose and fpaths_found:
            print(
                "The following files were polled and found: "
                f"{'; '.join(sorted(fpaths_found))}"
            )
        if fpaths_not_found:
            warnings.warn(
                "The following files were polled and NOT found: "
                f"{'; '.join(sorted(fpaths_not_found))}"
            )
        if self._return_found:
            return fpaths_found
        return None


class Input(NodeAwarePlugin):
    def __call__(self, filepath, node_properties=None, **kwargs):
        """
        Given a string, expand it and return this expanded string.

        Expand the provided string (typically representing a filepath) using the
        keyword arguments and environment variables.  Note that this plugin is
        'node aware' since it is derived from the `NodeAwarePlugin`.

        Args:
        - `filepath` (str): The filepath to be expanded.
        - `node_properties`: node properties passed by the plugin executor.
        - **kwargs: Keyword arguments to be used in the expansion.

        Returns:
        - str: The expanded filepath.

        Raises:
        - ValueError: If positional arguments are provided.
        """

        def expand(pstring):
            res = os.path.expanduser(
                string.Template(
                    pstring.format(**(kwargs | (node_properties or {})))
                ).substitute(os.environ)
            )
            if "{" in res and "}" in res:
                return expand(res)
            return res

        return expand(str(filepath))


class LoadJson(Load):
    """Load json file."""

    def load(self, *args):
        res = []
        for arg in args:
            with open(arg, "r") as f:
                res.append(json.load(f))
        return res[0] if len(res) == 1 else res


class SaveJson(Input):
    def __call__(self, *args, filepath, node_properties=None, **kwargs):
        """
        Save data to a JSON file

        Save the provided data to a JSON file at the specified filepath.  The filepath
        is expanded using the keyword arguments and environment variables.  Note that
        this plugin is 'node aware' since it is derived from the `NodeAwarePlugin`.

        Args:
        - `*args`: Positional arguments (data) to be saved.
        - `filepath`: The filepath to save the data to.
        - `node_properties`: node properties passed by the plugin executor.
        - `**kwargs`: Keyword arguments to be used in the expansion.

        Returns:
        - None
        """
        if not args:
            return None
        filepath = super().__call__(
            filepath=filepath, **(kwargs | (node_properties or {}))
        )
        with open(filepath, "w") as f:
            json.dump(args if len(args) > 1 else args[0], f)
        return None


class LoadPickle(Load):
    """Load pickle file."""

    def load(self, *args):
        res = []
        for arg in args:
            with open(arg, "rb") as f:
                res.append(pickle.load(f))
        return res[0] if len(res) == 1 else res


class SavePickle(Input):
    def __call__(self, *args, filepath, node_properties=None, **kwargs):
        """
        Save data to a Pickle file

        Save the provided data to a pickle file at the specified filepath.  The filepath
        is expanded using the keyword arguments and environment variables.  Note that
        this plugin is 'node aware' since it is derived from the `NodeAwarePlugin`.

        Args:
        - `*args`: Positional arguments (data) to be saved.
        - `filepath`: The filepath to save the data to.
        - `node_properties`: node properties passed by the plugin executor.
        - `**kwargs`: Keyword arguments to be used in the expansion.

        Returns:
        - None
        """
        if not args:
            return None
        node_properties = {} if node_properties is None else node_properties
        filepath = super().__call__(filepath=filepath, **(kwargs | node_properties))
        with open(filepath, "wb") as f:
            pickle.dump(args if len(args) > 1 else args[0], f)
        return None
