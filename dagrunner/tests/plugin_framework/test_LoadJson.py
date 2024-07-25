# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import json

import pytest

from dagrunner.plugin_framework import LoadJson


@pytest.fixture(scope="session")
def tmp_files(tmp_path_factory):
    """Create temporary JSON files."""
    tmp_dir = tmp_path_factory.mktemp("data")
    tmp_file1 = tmp_dir / "file1.json"
    tmp_file2 = tmp_dir / "file2.json"

    with open(tmp_file1, "w") as f:
        json.dump({"key1": "value1"}, f)
    with open(tmp_file2, "w") as f:
        json.dump({"key3": "value2"}, f)
    return tmp_file1, tmp_file2


def test_load_multiple_json(tmp_files):
    tmp_file1, tmp_file2 = tmp_files
    res = LoadJson()(tmp_file1, tmp_file2)
    assert res == [{"key1": "value1"}, {"key3": "value2"}]


def test_load_single_json(tmp_files):
    """Test loading a single JSON file doesn't return an iterable of results."""
    tmp_file1, _ = tmp_files
    res = LoadJson()(tmp_file1)
    assert res == {"key1": "value1"}
