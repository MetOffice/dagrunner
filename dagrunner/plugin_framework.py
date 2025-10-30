# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import itertools
import json
import os
import pickle
import string
import subprocess
import warnings
from abc import ABC, abstractmethod
from glob import glob

from dagrunner.utils import data_polling, process_path, stage_to_dir

from . import events


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


class Load(Plugin):
    def __init__(self, staging_dir=None, on_missing="error", verbose=False):
        """
        Load data from a file.

        The `load` method must be implemented by the subclass.

        Args:
        - staging_dir: Directory to stage files in.
        - on_missing: Action to take when files are missing. Accepted values: 'error',
          'ignore' and 'skip'.
        - verbose: Print verbose output.
        """
        self._staging_dir = staging_dir
        self._verbose = verbose
        self._on_missing = on_missing
        if self._on_missing not in ["error", "ignore", "skip"]:
            raise ValueError(
                f"Invalid value for 'on_missing': {self._on_missing}. "
                "Accepted values are 'error', 'ignore', and 'skip'."
            )

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

    def __call__(self, *args, **kwargs):
        """
        Load data from a file or list of files.

        Args:
        - *args: List of filepaths to load. `<hostname>:<path>` syntax supported
          for loading files from a remote host.
        - **kwargs: Keyword arguments to pass to.
        """
        args = list(map(process_path, args))
        if (
            any([arg.split(":")[0] for arg in args if ":" in arg])
            and self._staging_dir is None
        ):
            raise ValueError(
                "Staging directory must be specified for loading remote files."
            )

        try:
            if self._staging_dir and args:
                args = stage_to_dir(
                    *args, staging_dir=self._staging_dir, verbose=self._verbose
                )
            else:
                missing_files = [not glob(arg) for arg in args]
                if any(missing_files):
                    raise FileNotFoundError(
                        f"No such file or directory: {', '.join(missing_files)}"
                    )
        except FileNotFoundError as e:
            if self._on_missing == "error":
                raise e
            elif self._on_missing == "ignore":
                warnings.warn(str(e))
                return events.IGNORE_EVENT
            elif self._on_missing == "skip":
                warnings.warn(str(e))
                return events.SKIP_EVENT
            else:
                raise ValueError(
                    f"Invalid value for 'on_missing': {self._on_missing}. "
                    "Accepted values are 'error', 'ignore', and 'skip'."
                )

        return self.load(*args, **kwargs)


class DataPolling(Plugin):
    """A trigger plugin that completes when data is successfully polled."""

    def __init__(self, timeout=60 * 2, polling=1, file_count=None, verbose=False):
        self._timeout = timeout
        self._polling = polling
        self._file_count = file_count
        self._verbose = verbose

    def __call__(self, *args):
        args = data_polling(
            *args,
            timeout=self._timeout,
            polling=self._polling,
            file_count=self._file_count,
            fail_fast=True,
            verbose=self._verbose,
        )
        return


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
        # support for glob patterns
        args = list(itertools.chain.from_iterable(map(glob, args)))
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
