# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import os
import pickle
import tempfile
import warnings
from pathlib import Path

from dagrunner.config import CONFIG


class _PickleCache:
    def __init__(self, node_id, verbose=False):
        self._node_id = node_id
        self._verbose = verbose
        self._enabled = bool(CONFIG["dagrunner_runtime"].get("cache_enabled", False))
        self._pickle_filepath = CONFIG["dagrunner_runtime"].get("cache_dir", None)
        if self._enabled:
            if not self._pickle_filepath:
                self._pickle_filepath = Path(tempfile.gettempdir()) / "dagrunner_cache"
            self._pickle_filepath = Path(self._pickle_filepath) / f"{node_id}.pickle"
            warnings.warn(
                "This class is experimental and untested.  "
                "It may be removed in a future release.",
                DeprecationWarning,
            )

    @property
    def cache_available(self):
        return (
            self._enabled
            and self._pickle_filepath
            and os.path.exists(self._pickle_filepath)
        )

    @property
    def cache_filepath(self):
        return self._pickle_filepath

    @property
    def cache_enabled(self):
        return self._enabled

    def load(self):
        if (
            self._enabled
            and self._pickle_filepath
            and os.path.exists(self._pickle_filepath)
        ):
            if self._verbose:
                print(f"loading pickle for {self._node_id}")
            with open(self._pickle_filepath, "rb") as f:
                return pickle.load(f)

    def dump(self, res):
        if not self._enabled or not self._pickle_filepath:
            return
        self._pickle_filepath.parent.mkdir(parents=True, exist_ok=True)
        if self._verbose:
            print(f"saving to pickle: {self._pickle_filepath}")
        with open(self._pickle_filepath, "wb") as f:
            pickle.dump(res, f)
