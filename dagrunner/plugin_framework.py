# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import json
import os
import string
import subprocess
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
        while (
            patterns_found < len(args)
            and files_found < file_count
            and time_taken < timeout
        ):
            fpattern = args[indx]
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
                time.sleep(polling)
                time_taken += polling

        if patterns_found < len(args):
            raise RuntimeError(f"Timeout waiting for: '{fpattern}'")
        if verbose and fpaths_found:
            print(f"The following files were polled and found: {fpaths_found}")
        return None


class Input(NodeAwarePlugin):
    def __call__(self, *args, filepath=None, **kwargs):
        """
        Given a filepath, expand it and return this string

        Expand the provided filepath using the keyword arguments and environment
        variables.  Note that this plugin is 'node aware' since it is derived from the
        `NodeAwarePlugin`.

        Args:
        - *args: Positional arguments are not accepted.
        - filepath (str): The filepath to be expanded.
        - **kwargs: Keyword arguments to be used in the expansion.  Node
          properties/attributes are additionally included here as a node aware plugin.

        Returns:
        - str: The expanded filepath.

        Raises:
        - ValueError: If positional arguments are provided.
        """
        if args:
            raise ValueError("Input plugin does not accept positional arguments")
        return os.path.expanduser(
            string.Template(filepath.format(**kwargs)).substitute(os.environ)
        )


class SaveJson(Input):
    def __call__(self, *args, filepath=None, node_properties=None, **kwargs):
        """
        Save data to a JSON file

        Save the provided data to a JSON file at the specified filepath.  The filepath
        is expanded using the keyword arguments and environment variables.  Note that
        this plugin is 'node aware' since it is derived from the `NodeAwarePlugin`.

        Args:
        - *args: Positional arguments (data) to be saved.
        - filepath (str): The filepath to save the data to.
        - data (Any): The data to be saved.
        - **kwargs: Keyword arguments to be used in the expansion.  Node
          properties/attributes are additionally included here as a node aware plugin.

        Returns:
        - None
        """
        if not args:
            return None
        filepath = super().__call__(filepath=filepath, **(kwargs | node_properties))
        with open(filepath, "w") as f:
            json.dump(args, f)
        return None
