# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import json
import os
import pickle
import string
import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from glob import glob


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
    Copy input (pre-existing) filepaths to staging area and update paths.

    Ignore the copy if files exist unless existing files are older.
    """
    args = list(args)
    for ind, arg in enumerate(args):
        fpath = arg.split(":")[-1]
        fnme = os.path.basename(fpath)
        # copy files to the target location.
        rsync_command = ["rsync", "-au", arg, f"{staging_dir}/."]
        subprocess.run(rsync_command, check=True, text=True, capture_output=True)

        args[ind] = os.path.join(staging_dir, fnme)
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
        if any([":" in str(arg) for arg in args]) and staging_dir is None:
            raise ValueError(
                "Staging directory must be specified for loading remote files."
            )

        if staging_dir and args:
            os.makedirs(staging_dir, exist_ok=True)
            tmpdir = tempfile.TemporaryDirectory(
                dir=staging_dir,
            ).name
            os.makedirs(tmpdir, exist_ok=True)
            args = _stage_to_dir(*args, staging_dir=tmpdir, verbose=verbose)

        return self.load(*args, **kwargs)


class DataPolling(Plugin):
    def __call__(
        self, *args, timeout=60 * 2, polling=1, file_count=None, verbose=False
    ):
        """
        Poll for availability of files

        Poll for data and return when all are available or otherwise raise an
        exception if the timeout is reached.

        Args:
        - *args: Variable length argument list of file patterns to be checked.
          `<hostname>:<path>` syntax supported for files on a remote host.
        - timeout (int): Timeout in seconds (default is 120 seconds).
        - polling (int): Time interval in seconds between each poll (default is 1
          second).
        - file_count (int): Expected number of files to be found (default is None).
            If specified, the total number of files found can be greater than the
            number of arguments.  Each argument is expected to return a minimum of
            1 match each in either case.

        Returns:
        - None

        Raises:
        - RuntimeError: If the timeout is reached before all files are found.
        """
        time_taken = indx = patterns_found = files_found = 0
        fpaths_found = []
        file_count = len(args) if file_count is None else max(file_count, len(args))
        while time_taken < timeout:
            fpattern = str(args[indx])
            if ":" in fpattern:
                host, pattern = fpattern.split(":")
                # bash equivalent to python glob (glob on remote host)
                print(f"ssh {host} \"printf '%s\n' {pattern} | grep -v '*'\" || true")
                expanded_paths = (
                    subprocess.run(
                        f"ssh {host} \"printf '%s\n' {pattern} | grep -v '*'\" || true",
                        shell=True,
                        check=True,
                        text=True,
                        capture_output=True,
                    )
                    .stdout.strip()
                    .split("\n")
                )
                print(f"expanded_paths: {expanded_paths}")
            else:
                expanded_paths = glob(fpattern)
            if expanded_paths:
                fpaths_found.extend(expanded_paths)
                patterns_found += 1
                files_found += len(expanded_paths)
                indx += 1
            elif verbose:
                print(
                    f"polling for '{fpattern}', time taken: {time_taken}s of limit "
                    f"{timeout}s"
                )
            if patterns_found >= len(args) or files_found >= file_count:
                break
            time.sleep(polling)
            time_taken += polling

        if patterns_found < len(args):
            raise FileNotFoundError(f"Timeout waiting for: '{fpattern}'")
        if verbose and fpaths_found:
            print(f"The following files were polled and found: {fpaths_found}")
        return None


class Input(NodeAwarePlugin):
    def __call__(self, filepath, **kwargs):
        """
        Given a filepath, expand it and return this string

        Expand the provided filepath using the keyword arguments and environment
        variables.  Note that this plugin is 'node aware' since it is derived from the
        `NodeAwarePlugin`.

        Args:
        - filepath (str): The filepath to be expanded.
        - **kwargs: Keyword arguments to be used in the expansion.  Node
          properties/attributes are additionally included here as a node aware plugin.

        Returns:
        - str: The expanded filepath.

        Raises:
        - ValueError: If positional arguments are provided.
        """

        def expand(pstring):
            res = os.path.expanduser(
                string.Template(pstring.format(**kwargs)).substitute(os.environ)
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
        node_properties = {} if node_properties is None else node_properties
        filepath = super().__call__(filepath=filepath, **(kwargs | node_properties))
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
