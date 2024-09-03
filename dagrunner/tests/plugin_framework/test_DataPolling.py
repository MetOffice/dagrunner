# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import socket
from unittest.mock import patch

import pytest

from dagrunner.plugin_framework import DataPolling


@pytest.fixture(scope="session")
def tmp_file(tmp_path_factory):
    """Create a temporary file."""
    tmp_file = tmp_path_factory.mktemp("data") / "test.txt"
    tmp_file.write_text("test")
    return tmp_file


def call_dp(filepath, verbose=True, **kwargs):
    dp = DataPolling()
    dp(filepath, timeout=0.001, polling=0.002, verbose=verbose, **kwargs)


def test_find_file(tmp_file, capsys):
    """Finding the file - basic usage."""
    call_dp(tmp_file)
    captured = capsys.readouterr()
    assert f"The following files were polled and found: ['{tmp_file}']" in captured.out


def test_missing_file():
    """Reaching timeout after not finding the file."""
    filepath = "/dummy/file/path.dat"
    msg = f"Timeout waiting for: '{filepath}'"
    with pytest.raises(FileNotFoundError, match=msg):
        call_dp(filepath, verbose=False)


def test_globular_pattern_matching(tmp_file, capsys):
    glob_tmp_file = tmp_file.parent / "*.txt"
    call_dp(glob_tmp_file)
    captured = capsys.readouterr()
    assert f"The following files were polled and found: ['{tmp_file}']" in captured.out


def test_specified_host(tmp_file, capsys):
    """<host>:<filepath>"""
    host_tmp_file = f"{socket.gethostname()}:{tmp_file}"
    # Mocking gethostname() so that our host doesn't match against our local host check
    # internally.
    with patch(
        "dagrunner.utils.socket.gethostname", return_value="dummy_host.dummy_domain"
    ):
        call_dp(host_tmp_file)
    captured = capsys.readouterr()
    assert f"The following files were polled and found: ['{tmp_file}']" in captured.out


def test_specified_host_missing_file(capsys):
    """<host>:<filepath>"""
    filepath = "/dummy/file/path.dat"
    host_tmp_file = f"{socket.gethostname()}:{filepath}"
    # Mocking gethostname() so that our host doesn't match against our local host check
    # internally.
    msg = f"Timeout waiting for: '{filepath}'"
    with patch(
        "dagrunner.utils.socket.gethostname", return_value="dummy_host.dummy_domain"
    ):
        with pytest.raises(FileNotFoundError, match=msg):
            call_dp(host_tmp_file, verbose=False)
