# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import socket
import subprocess
from glob import glob
from unittest.mock import patch

import pytest

from dagrunner.utils import data_polling


@pytest.fixture(scope="session")
def tmp_files(tmp_path_factory):
    """Create temporary files."""
    tmp_dir = tmp_path_factory.mktemp("data")
    tmp_file1 = tmp_dir / "test1.txt"
    tmp_file1.write_text("test")
    tmp_file2 = tmp_dir / "test2.txt"
    tmp_file2.write_text("test")
    return tmp_file1, tmp_file2


def call_dp(*filepaths, verbose=True, **kwargs):
    return data_polling(*filepaths, timeout=0, polling=0, verbose=verbose, **kwargs)


def test_find_file(tmp_files, capsys):
    """Finding the file - basic usage."""
    tmp_file, _ = tmp_files
    res = call_dp(tmp_file)
    assert list(res) == [str(tmp_file)]


def test_find_multiple_file(tmp_files):
    tmp_files = list(map(str, tmp_files))
    res = call_dp(*tmp_files)
    assert sorted(tmp_files) == sorted(res)


def test_globular_pattern_matching(tmp_files):
    tmp_file, _ = tmp_files
    glob_tmp_file = tmp_file.parent / "*.txt"
    res = call_dp(glob_tmp_file)
    assert sorted(map(str, tmp_files)) == sorted(res)


def test_missing_file():
    """Reaching timeout after not finding the file."""
    filepath = "/dummy/file/path.dat"
    msg = f"Timeout waiting for: {filepath}"
    with pytest.raises(FileNotFoundError, match=msg):
        call_dp(filepath, verbose=False)


def test_missing_file_non_zero_poll():
    """Reaching timeout after not finding the file."""
    filepath = "/dummy/file/path.dat"
    msg = f"Timeout waiting for: {filepath}"
    with pytest.raises(FileNotFoundError, match=msg):
        data_polling(filepath, timeout=0.2, polling=0.1, verbose=False)


def test_specified_host(tmp_files):
    """<host>:<filepath>"""
    tmp_file, _ = tmp_files
    host_tmp_file = f"{socket.gethostname()}:{tmp_file}"
    # Mocking gethostname() so that our host doesn't match against our local host check
    # internally.  If gethostname matches the local host check, it removes the host and
    # uses python glob.
    with patch(
        "dagrunner.utils.socket.gethostname", return_value="dummy_host.dummy_domain"
    ):
        res = call_dp(host_tmp_file)
    assert list(res) == [host_tmp_file]


def test_specified_host_missing_file():
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


def test_mixture_of_hosts_local(tmp_dir):
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
                f"{socket.gethostname()}:{tmp_dir / 'testA0.txt'}",
                f"{socket.gethostname()}:{tmp_dir / 'testA1.txt'}",
                f"{socket.gethostname()}:{tmp_dir / 'testB0.txt'}",
                f"{socket.gethostname()}:{tmp_dir / 'testB1.txt'}",
                f"{tmp_dir / 'testC0.txt'}",
                f"{tmp_dir / 'testC1.txt'}",
                f"{tmp_dir / 'testD0.txt'}",
                f"{tmp_dir / 'testD1.txt'}",
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
        with patch("dagrunner.utils.glob", wraps=glob) as mock_glob:
            with patch(
                "dagrunner.utils.subprocess.run", wraps=subprocess.run
            ) as mock_subprocrun:
                res = call_dp(*input_paths)

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

    assert sorted(res) == sorted(target)
