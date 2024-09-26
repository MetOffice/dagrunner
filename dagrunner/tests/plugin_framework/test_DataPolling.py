# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import socket
import subprocess
from glob import glob
from unittest.mock import patch

import pytest

from dagrunner.plugin_framework import DataPolling


@pytest.fixture(scope="session")
def tmp_file(tmp_path_factory):
    """Create a temporary file."""
    tmp_file = tmp_path_factory.mktemp("data") / "test.txt"
    tmp_file.write_text("test")
    return tmp_file


def call_dp(*filepaths, verbose=True, **kwargs):
    dp = DataPolling()
    # dp(*filepaths, timeout=0.001, polling=0.002, verbose=verbose, **kwargs)
    dp(*filepaths, timeout=0, polling=0, verbose=verbose, **kwargs)


def test_find_file(tmp_file, capsys):
    """Finding the file - basic usage."""
    call_dp(tmp_file)
    captured = capsys.readouterr()
    assert f"The following files were polled and found: {tmp_file}" in captured.out


def test_missing_file():
    """Reaching timeout after not finding the file."""
    filepath = "/dummy/file/path.dat"
    msg = f"Timeout waiting for: {filepath}"
    with pytest.raises(FileNotFoundError, match=msg):
        call_dp(filepath, verbose=False)


def test_globular_pattern_matching(tmp_file, capsys):
    glob_tmp_file = tmp_file.parent / "*.txt"
    call_dp(glob_tmp_file)
    captured = capsys.readouterr()
    assert f"The following files were polled and found: {tmp_file}" in captured.out


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
    assert f"The following files were polled and found: {tmp_file}" in captured.out


def test_specified_host_missing_file(capsys):
    """<host>:<filepath>"""
    filepath = "/dummy/file/path.dat"
    host_tmp_file = f"{socket.gethostname()}:{filepath}"
    # Mocking gethostname() so that our host doesn't match against our local host check
    # internally.
    msg = f"Timeout waiting for: {socket.gethostname()}:{filepath}"
    with patch(
        "dagrunner.utils.socket.gethostname", return_value="dummy_host.dummy_domain"
    ):
        with pytest.raises(FileNotFoundError, match=msg):
            call_dp(host_tmp_file, verbose=False)


@pytest.fixture(scope="session")
def tmp_dir(tmp_path_factory):
    """Create a temporary file."""
    tmp_file = tmp_path_factory.mktemp("data")
    for i in range(2):
        tfile = tmp_file / f"testA{i}.txt"
        tfile.write_text(f"test{i}")
    for i in range(2):
        tfile = tmp_file / f"testB{i}.txt"
        tfile.write_text(f"test{i}")
    for i in range(2):
        tfile = tmp_file / f"testC{i}.txt"
        tfile.write_text(f"test{i}")
    for i in range(2):
        tfile = tmp_file / f"testD{i}.txt"
        tfile.write_text(f"test{i}")
    return tmp_file


def test_mixture_of_hosts_local(tmp_dir, capsys):
    """
    Ensure that we can poll for groups of shared inputs by common host and whether
    they are globular or not.
    """
    input_paths = [
        f"{socket.gethostname()}:{tmp_dir / 'testA0.txt'}",
        f"{socket.gethostname()}:{tmp_dir / 'testA1.txt'}",
        f"{socket.gethostname()}:{tmp_dir / 'testB*.txt'}",
        f"{tmp_dir / 'testC0.txt'}",
        f"{tmp_dir / 'testC1.txt'}",
        f"{tmp_dir / 'testD*.txt'}",
    ]

    target = {
        str(pp)
        for pp in sorted(
            [
                tmp_dir / "testA0.txt",
                tmp_dir / "testA1.txt",
                tmp_dir / "testB0.txt",
                tmp_dir / "testB1.txt",
                tmp_dir / "testC0.txt",
                tmp_dir / "testC1.txt",
                tmp_dir / "testD0.txt",
                tmp_dir / "testD1.txt",
            ]
        )
    }

    # Mocking gethostname() so that our host doesn't match against our local host check
    # internally.
    with patch(
        "dagrunner.utils.socket.gethostname", return_value="dummy_host.dummy_domain"
    ):
        # patch plugin_framework.glob with a wrapper so that we can check what
        # it was called with.
        with patch("dagrunner.plugin_framework.glob", wraps=glob) as mock_glob:
            with patch(
                "dagrunner.plugin_framework.subprocess.run", wraps=subprocess.run
            ) as mock_subprocrun:
                call_dp(*input_paths)

    # check how subprocess.run was called
    #####################################
    assert len(mock_subprocrun.call_args_list) == 2

    # group all non glob patterns into a single call (minimising ssh calls)
    for res_index, targets in zip(
        range(2),
        [[f"{tmp_dir}/testA0.txt", f"{tmp_dir}/testA1.txt"], [f"{tmp_dir}/testB*.txt"]],
    ):
        objcall = mock_subprocrun.call_args_list[res_index]
        results = objcall[0][0].replace(";", "").split()
        assert (
            sorted(filter(lambda substr: substr.startswith(str(tmp_dir)), results))
            == targets
        )

    # check how glob was called (glob supports only 1 path arguments)
    #####################################
    assert len(mock_glob.call_args_list) == 3
    targets = [
        f"{tmp_dir}/testC0.txt",
        f"{tmp_dir}/testC1.txt",
        f"{tmp_dir}/testD*.txt",
    ]
    for objcall in mock_glob.call_args_list:
        assert objcall[0][0] in targets
        targets.remove(objcall[0][0])

    captured = capsys.readouterr()
    assert (
        f"The following files were polled and found: {'; '.join(sorted(target))}"
        in captured.out
    )
