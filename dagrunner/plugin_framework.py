# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import json
import os
import pickle
import shutil
import string
import subprocess
import warnings
from abc import ABC, abstractmethod
from glob import glob

from dagrunner.utils import process_path, Singleton, data_polling, stage_to_dir


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


class Load(Plugin):
    def __init__(self, staging_dir=None, ignore_missing=False, verbose=False):
        """
        Load data from a file.

        The `load` method must be implemented by the subclass.

        Args:
        - staging_dir: Directory to stage files in.
        - verbose: Print verbose output.
        """
        self._staging_dir = staging_dir
        self._verbose = verbose
        self._ignore_missing = ignore_missing

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

        if self._staging_dir and args:
            try:
                args = stage_to_dir(*args, staging_dir=self._staging_dir, verbose=self._verbose)
            except FileNotFoundError as e:
                if self._ignore_missing:
                    warnings.warn(str(e))
                    return SKIP_EVENT
                raise e
        else:
            missing_files = [not os.path.exists(arg) for arg in args]
            if any(missing_files):
                if self._ignore_missing:
                    warnings.warn("Ignoring missing files.")
                    return SKIP_EVENT
                else:
                    raise FileNotFoundError(
                        f"Missing files: {', '.join(missing_files)}"
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
            fpaths_found, fpaths_not_found = data_polling(*args, self._timeout, self._polling, self._file_count, fail_fast=True, verbose=self._verbose)
            if fpaths_not_found:
                raise FileNotFoundError(
                    f"Timeout waiting for: {'; '.join(sorted(fpaths_not_found))}"
                )
            if self._verbose:
                msg = f"These files were polled and found: {'; '.join(sorted(fpaths_found))}"
                print(msg)
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
