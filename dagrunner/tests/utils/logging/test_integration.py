# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import logging
import os
import sqlite3
import subprocess

import pytest

from dagrunner.utils.logger import ServerContext


@pytest.fixture
def sqlite_filepath(tmp_path):
    return tmp_path / "test_logs.sqlite"


def gen_client_code(loggers):
    code = "import logging;"
    code += "from dagrunner.utils.logger import client_attach_socket_handler;"
    code += "client_attach_socket_handler();"

    for msg, lvlname, name in loggers:
        if lvlname:
            code += f"logging.getLogger('{lvlname}').{name}('{msg}');"
        else:
            code += f"logging.{name}('{msg}');"
    return code


def test_sqlitedb(sqlite_filepath, caplog):
    test_inputs = (
        ["Python is versatile and powerful.", "root", "info"],
        ["Lists store collections of items.", "myapp.area1", "debug"],
        ["Functions encapsulate reusable code.", "myapp.area1", "info"],
        ["Indentation defines code blocks.", "myapp.area2", "warning"],
        ["Libraries extend Pythons capabilities.", "myapp.area2", "error"],
    )
    client_code = gen_client_code(test_inputs)
    with ServerContext(sqlite_filepath=sqlite_filepath, verbose=True):
        subprocess.run(
            ["python", "-c", client_code], capture_output=True, text=True, check=True
        )

    # Check log messages
    assert len(caplog.record_tuples) == len(test_inputs)
    for test_input, record in zip(test_inputs, caplog.record_tuples):
        assert (
            tuple(
                [test_input[1], getattr(logging, test_input[2].upper()), test_input[0]]
            )
            == record
        )

    # Check there are any records in the database
    conn = sqlite3.connect(sqlite_filepath)
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
