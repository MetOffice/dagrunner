# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import json
import os
import socket
from glob import glob
from unittest.mock import patch

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
    assert sorted(res, key=lambda x: list(x.keys())) == sorted(
        [{"key1": "value1"}, {"key3": "value2"}], key=lambda x: list(x.keys())
    )


def test_load_single_json(tmp_files):
    """Test loading a single JSON file doesn't return an iterable of results."""
    tmp_file1, _ = tmp_files
    res = LoadJson()(tmp_file1)
    assert res == {"key1": "value1"}


def test_load_glob_json(tmp_files):
    """Test loading multiple JSON files using glob pattern."""
    tmp_file1, tmp_file2 = tmp_files
    res = LoadJson()(str(tmp_file1.parent / "*.json"))
    assert sorted(res, key=lambda x: list(x.keys())) == sorted(
        [{"key1": "value1"}, {"key3": "value2"}], key=lambda x: list(x.keys())
    )


def test_load_remote_not_staged():
    """Test loading a remote file that isn't setup to be staged."""
    with pytest.raises(
        ValueError,
        match="Staging directory must be specified for loading remote files.",
    ):
        LoadJson()("host:file.json")


@pytest.fixture()
def staged_directory(tmp_path_factory):
    """Create a staging directory."""
    tmp_dir = tmp_path_factory.mktemp("staging")
    return tmp_dir


def test_load_remote_rsync(tmp_files, staged_directory):
    """Test loading a remote file that has been staged using rsync."""
    tmp_file1, _ = tmp_files
    # Mocking gethostname() so that our host doesn't match against our local host check
    # internally.
    fpath = f"{socket.gethostname()}:{str(tmp_file1)}"
    with patch(
        "dagrunner.utils.socket.gethostname", return_value="dummy_host.dummy_domain"
    ):
        res = LoadJson(staging_dir=staged_directory)(fpath)
    assert res == {"key1": "value1"}
    staged_files = glob(str(staged_directory / f"*_{tmp_file1.name}"))
    assert len(staged_files) == 1
    # ensure it IS NOT a hardlink file
    assert os.stat(staged_files[0]).st_nlink == 1


def test_load_local_staged_hardlink(tmp_files, staged_directory):
    """Test staging a local file, hardlinking that file."""
    tmp_file1, _ = tmp_files
    res = LoadJson(staging_dir=staged_directory)(tmp_file1)
    assert res == {"key1": "value1"}
    staged_files = glob(str(staged_directory / f"*_{tmp_file1.name}"))
    assert len(staged_files) == 1
    # ensure it IS a hardlink file
    assert os.stat(staged_files[0]).st_nlink == 2
