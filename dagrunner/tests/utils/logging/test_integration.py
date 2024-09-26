# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import inspect
import logging
import os
import sqlite3
import subprocess
import sys
import time

import pytest

import dagrunner
from dagrunner.utils.logger import client_attach_socket_handler


@pytest.fixture
def sqlite_filepath(tmp_path):
    return tmp_path / "test_logs.sqlite"


@pytest.fixture
def server(sqlite_filepath):
    pythonpath = os.path.dirname(os.path.dirname(inspect.getfile(dagrunner)))
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.path.dirname(__file__)}/../../../utils/:{pythonpath}"

    # Start the server process
    server_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "logger",
            "--sqlite-filepath",
            str(sqlite_filepath),
            "--verbose",
        ],
        env=env,
    )

    # Wait for the server to start (adjust as needed)
    time.sleep(1)  # Can use a more robust method to check server readiness

    yield server_proc, sqlite_filepath

    # Teardown: Kill the server after tests are done
    server_proc.terminate()
    server_proc.wait()


def test_sqlitedb(server, caplog):
    test_inputs = (
        ["Python is versatile and powerful.", "root", "info"],
        ["Lists store collections of items.", "myapp.area1", "debug"],
        ["Functions encapsulate reusable code.", "myapp.area1", "info"],
        ["Indentation defines code blocks.", "myapp.area2", "warning"],
        ["Libraries extend Pythons capabilities.", "myapp.area2", "error"],
    )
    client_attach_socket_handler()
    for msg, lvlname, name in test_inputs:
        getattr(logging.getLogger(lvlname), name)(msg)

    # Check log messages
    assert len(caplog.record_tuples) == len(test_inputs)
    for test_input, record in zip(test_inputs, caplog.record_tuples):
        assert (
            tuple(
                [test_input[1], getattr(logging, test_input[2].upper()), test_input[0]]
            )
            == record
        )

    server_proc, sqlite_filepath = server
    time.sleep(1)  # wait for db write to complete
    server_proc.terminate()

    # Check there are any records in the database
    conn = sqlite3.connect(str(sqlite_filepath))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs")
    count = cursor.fetchone()[0]
    assert count > 0, "At least one log record should be stored in the database"

    # Verify database records
    # (record.created, record.name, record.levelname, record.getMessage(),
    #  record.hostname, record.process, record.thread)
    # Verify against expected values and ensure dynamic values are of the expected
    # type.
    records = cursor.execute("SELECT * FROM logs").fetchall()
    for test_input, record in zip(test_inputs, records):
        tar_format = (
            float,
            test_input[1],
            test_input[2].upper(),
            test_input[0],
            os.uname().nodename,
            int,
            int,
        )

        assert len(record) == len(tar_format)
        for tar, rec in zip(tar_format, record):
            if isinstance(tar, type):
                # simply check it is the correct type
                assert type(eval(rec)) is tar
            else:
                assert rec == tar
    conn.close()
