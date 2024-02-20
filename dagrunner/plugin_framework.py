# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'pp_systems_framework' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from abc import ABC, abstractmethod
import os
from glob import glob
import string
import subprocess
import time


class Plugin(ABC):
    """Abstract base class to define our plugin UI"""

    @abstractmethod
    def __call__(self, *args, verbose=False, **kwargs):
        raise NotImplementedError


class NodeAwarePlugin(ABC):
    """A plugin that is of type instructed to be passed node parameters"""

    @abstractmethod
    def __call__(self, *args, verbose=False, **kwargs):
        raise NotImplementedError


class Shell(Plugin):
    def __call__(self, *args, verbose=False, **kwargs):
        return subprocess.run(*args, **kwargs, shell=True, check=True)


class DataPolling(Plugin):
    def __call__(self, *args, timeout=60*2, polling=1, file_count=None, verbose=False):
            """
            Poll for availability of files
            
            Poll for data and return when all are available or otherwise raise an
            exception if the timeout is reached.
            
            Args:
                *args: Variable length argument list of file patterns to be checked.
                timeout (int): Timeout in seconds (default is 120 seconds).
                polling (int): Time interval in seconds between each poll (default is 1 second).
                file_count (int): Expected number of files to be found (default is None).
                    If specified, the total number of files found can be greater than the
                    number of arguments.  Each argument is expected to return a minimum of
                    1 match each in either case.
                verbose (bool): If True, print additional information during polling (default is False).
            
            Returns:
                None
            
            Raises:
                RuntimeError: If the timeout is reached before all files are found.
            """
            time_taken = indx = patterns_found = files_found = 0
            fpaths_found = []
            file_count = len(args) if file_count is None else max(file_count, len(args))
            while patterns_found < len(args) and files_found < file_count and time_taken < timeout:
                fpattern = args[indx]
                expanded_paths = glob(fpattern)
                if expanded_paths:
                    fpaths_found.extend(expanded_paths)
                    patterns_found += 1
                    files_found += len(expanded_paths)
                    indx += 1
                elif verbose:
                    print(f"polling for '{fpattern}', time taken: {time_taken}s of limit {timeout}s")
                    time.sleep(polling)
                    time_taken += polling

            if patterns_found < len(args):
                raise RuntimeError(f"Timeout waiting for: '{fpattern}'")
            if verbose and fpaths_found:
                print(f"The following files were polled and found: {fpaths_found}")
            return None


class Input(NodeAwarePlugin):
    def __call__(self, *args, filepath=None, verbose=False, **kwargs):
        if args:
            raise ValueError("Input plugin does not accept positional arguments")
        target_fmt = filepath.format
        return os.path.expanduser(string.Template(filepath.format(**kwargs)).substitute(os.environ))
