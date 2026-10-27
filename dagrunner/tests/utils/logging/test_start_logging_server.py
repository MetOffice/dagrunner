# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""Check logging-server cleanup both in isolation and in a real process.

Mocked tests verify resource ownership, cleanup order, exception propagation, and
restoration of the caller's signal handlers. Subprocess tests deliver real signals
without risking termination of pytest and check that shutdown drains complete
records without waiting for clients to disconnect.
"""

import logging
import signal
import socket
import sqlite3
import struct
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

from dagrunner.utils.logger import start_logging_server

from ._logging_test_helpers import wait_for_logging_server_port


@pytest.mark.parametrize("signum", [signal.SIGINT, signal.SIGTERM])
@pytest.mark.parametrize("sqlite_filepath", [None, "logs.sqlite"])
def test_signal_cleanup(signum, sqlite_filepath):
    """Both termination signals clean up with or without SQLite enabled."""
    original_handlers = {
        sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)
    }
    # Use a real logging.Handler so root-logger attachment behaves normally,
    # while mocking close lets us check its timing and call count.
    sqlite_handler = logging.NullHandler()
    sqlite_handler.close = Mock()
    with (
        patch("dagrunner.utils.logger.LogRecordSocketReceiver") as receiver,
        patch("dagrunner.utils.logger.SQLiteHandler", return_value=sqlite_handler),
    ):
        # The server used by start_logging_server is the context manager's value.
        server = receiver.return_value.__enter__.return_value

        def terminate():
            # Invoke the installed callback directly rather than signalling pytest.
            signal.getsignal(signum)(signum, None)
            assert server.abort == 1
            if sqlite_filepath:
                assert sqlite_handler in logging.getLogger("").handlers
                sqlite_handler.close.assert_not_called()

        server.serve_until_stopped.side_effect = terminate
        if sqlite_filepath:
            # Closing SQLite must follow server context exit, which waits for
            # request threads that may still be writing log records.
            sqlite_handler.close.side_effect = (
                receiver.return_value.__exit__.assert_called_once
            )
        start_logging_server(sqlite_filepath=sqlite_filepath)

        receiver.return_value.__exit__.assert_called_once()
        assert server.abort == 1
        assert sqlite_handler not in logging.getLogger("").handlers
        if sqlite_filepath:
            sqlite_handler.close.assert_called_once()
        else:
            sqlite_handler.close.assert_not_called()
    for sig, handler in original_handlers.items():
        assert signal.getsignal(sig) == handler


@pytest.mark.parametrize("failure", ["serve", "sqlite"])
def test_exception_cleanup(failure):
    """Setup and serving failures propagate after releasing acquired resources.

    A SQLite construction failure still closes the server, but there is no
    completed SQLite handler to detach or close.
    """
    original_handlers = {
        sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)
    }
    sqlite_handler = logging.NullHandler()
    sqlite_handler.close = Mock()
    with (
        patch("dagrunner.utils.logger.LogRecordSocketReceiver") as receiver,
        patch(
            "dagrunner.utils.logger.SQLiteHandler", return_value=sqlite_handler
        ) as handler_factory,
    ):
        server = receiver.return_value.__enter__.return_value
        if failure == "serve":
            server.serve_until_stopped.side_effect = RuntimeError("server failed")
        else:
            handler_factory.side_effect = RuntimeError("sqlite failed")

        message = "server failed" if failure == "serve" else "sqlite failed"
        with pytest.raises(RuntimeError, match=message):
            start_logging_server(sqlite_filepath="logs.sqlite")

        receiver.return_value.__exit__.assert_called_once()
        assert sqlite_handler not in logging.getLogger("").handlers
        if failure == "serve":
            sqlite_handler.close.assert_called_once()
    for sig, handler in original_handlers.items():
        assert signal.getsignal(sig) == handler


@pytest.mark.parametrize("signum", [signal.SIGINT, signal.SIGTERM])
@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(b"", id="connected-without-data"),
        pytest.param(b"\x00", id="one-byte-of-four-byte-header"),
        pytest.param(struct.pack(">L", 100) + b"x", id="one-byte-of-100-byte-record"),
    ],
)
def test_process_termination(tmp_path, signum, payload):
    """Shutdown drains complete records without waiting on incomplete ones.

    ``payload`` is the raw TCP data sent by the test client, not a log message.
    The logging protocol expects a four-byte big-endian record length followed by
    that many bytes of pickled log-record data. These cases deliberately withhold
    data the server would normally wait for:

    - ``b""``: send nothing, leaving the server waiting for a length header.
    - ``b"\\x00"``: send only one of the four required header bytes.
    - ``struct.pack(">L", 100) + b"x"``: announce a 100-byte record but send
      only one body byte, leaving another 99 bytes outstanding.

    Complete records precede each payload and must all reach SQLite. No database
    polling or commit wait is needed before sending the signal. The client stays
    connected until after server exit, proving shutdown does not depend on client
    cleanup. An incomplete trailing record cannot be stored and is discarded.
    """
    database = tmp_path / "logs.sqlite"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "dagrunner.utils.logger",
            "--port",
            "0",
            "--sqlite-filepath",
            str(database),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    client = None
    try:
        port = wait_for_logging_server_port(process)
        client = socket.create_connection(("localhost", port), timeout=5)
        assert database.exists(), "SQLite handler did not initialise"
        encoder = logging.handlers.SocketHandler("localhost", port)
        messages = [f"Record {index}" for index in range(5)]
        for message in messages:
            record = logging.makeLogRecord(
                {"name": "shutdown-test", "levelno": logging.INFO, "msg": message}
            )
            client.sendall(encoder.makePickle(record))
        if payload:
            client.sendall(payload)
        process.send_signal(signum)
        output, _ = process.communicate(timeout=5)
        assert process.returncode == 0, output.decode()
        # Rebinding checks that the listening socket was released; SO_REUSEADDR
        # avoids treating TCP's normal TIME_WAIT state as a leaked socket.
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(("localhost", port))
        with sqlite3.connect(database) as connection:
            records = connection.execute("SELECT message FROM logs ORDER BY rowid")
            assert [row[0] for row in records] == messages
            assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    finally:
        # Bound teardown even if a readiness or shutdown assertion fails, so a
        # broken server cannot leave a child process behind or hang pytest.
        if client is not None:
            client.close()
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)
