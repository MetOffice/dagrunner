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
        self._pickle_filepath = CONFIG["dagrunner_runtime"].get("cache_dir", None)
        enabled = bool(CONFIG["dagrunner_runtime"].get("cache_enabled", False))
        if not self._pickle_filepath and enabled:
            self._pickle_filepath = Path(tempfile.gettempdir()) / "dagrunner_cache"
        if self._pickle_filepath is not None:
            self._pickle_filepath = Path(self._pickle_filepath) / f"{node_id}.pickle"
            warnings.warn(
                "This class is experimental and untested.  "
                "It may be removed in a future release.",
                DeprecationWarning,
            )

    def load(self):
        if self._pickle_filepath is not None and os.path.exists(self._pickle_filepath):
            if self._verbose:
                print(f"loading pickle for {self._node_id}")
            with open(self._pickle_filepath, "rb") as f:
                return pickle.load(f)

    def dump(self, res):
        if self._pickle_filepath is None:
            return
        self._pickle_filepath.parent.mkdir(parents=True, exist_ok=True)
        if self._verbose:
            print(f"saving to pickle: {self._pickle_filepath}")
        with open(self._pickle_filepath, "wb") as f:
            pickle.dump(res, f)
