#!/usr/bin/env python3
# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
This module takes much from the Python logging cookbook:
https://docs.python.org/3/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

## Overview

- `client_attach_socket_handler`, a function that attaches a socket handler
  `logging.handlers.SocketHandler` to the root logger with the specified host name and
  port number.
- `start_logging_server`, a function to start the TCP server
  `LogRecordSocketReceiver` on its own thread, ready to receive log records.
  - `SQLiteHandler`, a custom logging handler to write log messages to an SQLite
    database.
  - `LogRecordSocketReceiver(socketserver.ThreadingTCPServer)`, the TCP server running
    on a specified host and port, managed by the server context that receives log
    records and utilises the `LogRecordStreamHandler` handler.
    - `LogRecordStreamHandler`, a specialisation of the
      `socketserver.StreamRequestHandler`, responsible for 'getting' log records.
"""

import datetime
import logging
import logging.handlers
import os
import pickle
import select
import signal
import socket
import socketserver
import sqlite3
import struct

from dagrunner.utils import function_to_argparse_parse_args

__all__ = ["client_attach_socket_handler", "start_logging_server"]


DATEFMT = "%Y-%m-%dT%H:%M:%S"  # Date in ISO 8601 format


def client_attach_socket_handler(
    host: str = "localhost",
    port: int = logging.handlers.DEFAULT_TCP_LOGGING_PORT,
    name: str = "",
):
    """
    Attach a SocketHandler instance to the named logger at the sending end.

    Now, we can log to the named logger, or any other logger. First the root...
        logging.info('Jackdaws love my big sphinx of quartz.')

    Now, define a couple of other loggers which might represent areas in your
    application:

        logger1 = logging.getLogger('myapp.area1')
        logger2 = logging.getLogger('myapp.area2')

        logger1.debug('Quick zephyrs blow, vexing daft Jim.')
        logger1.info('How quickly daft jumping zebras vex.')
        logger2.warning('Jail zesty vixen who grabbed pay from quack.')
        logger2.error('The five boxing wizards jump quickly.')

    Args:
    - `host`: The host name of the server.  Optional.
    - `port`: The port number the server is listening on.  Optional.
    - `name`: The name of the logger to attach the socket handler to.  Optional.
              If `name` is not specified, the socket handler is attached to the
              root logger as per `logging.getLogger("")`

    """
    rootLogger = logging.getLogger(name)
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler(host, port)
    # don't bother with a formatter, since a socket handler sends the event as
    # an unformatted pickle
    rootLogger.addHandler(socketHandler)


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """
    Handler for a streaming logging request.

    Specialisation of the `socketserver.StreamRequestHandler` class to handle log
    records and customise logging events.
    """

    def _recv(self, size):
        """Receive exactly ``size`` bytes, draining available data on shutdown.

        Poll during normal operation so idle clients cannot block shutdown.
        Once stopping, read only immediately available bytes instead of waiting
        for clients to send more or disconnect. Return ``b""`` on disconnect
        or when shutdown leaves an incomplete record.
        """
        chunks = bytearray()
        while len(chunks) < size:
            timeout = 0 if self.server.abort else self.server.timeout
            readable, _, _ = select.select([self.connection], [], [], timeout)
            if not readable:
                if self.server.abort:
                    return b""
                continue
            chunk = self.connection.recv(size - len(chunks))
            if not chunk:
                return b""
            chunks.extend(chunk)
        return bytes(chunks)

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self._recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self._recv(slen)
            if not chunk:
                break
            obj = self.unpickle(chunk)
            record = logging.makeLogRecord(obj)
            record.hostname = socket.gethostname()
            self.handle_log_record(record)

    def unpickle(self, data):
        return pickle.loads(data)

    def handle_log_record(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver.

    Specialisation of the `socketserver.ThreadingTCPServer` class to handle
    log records.
    """

    allow_reuse_address = True

    def __init__(
        self,
        host="localhost",
        port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
        handler=LogRecordStreamHandler,
    ):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        """Accept requests until stopped, including connections already queued."""
        while True:
            timeout = 0 if self.abort else self.timeout
            rd, wr, ex = select.select([self.socket.fileno()], [], [], timeout)
            if rd:
                self.handle_request()
            elif self.abort:
                break


class SQLiteHandler(logging.Handler):
    """
    Custom logging handler to write log messages to an SQLite database.
    """

    def __init__(self, sqfile="logs.sqlite"):
        logging.Handler.__init__(self)
        self._sqfile = sqfile
        self._create_table()

    def _create_table(self):
        """
        Creates a table to store the logs if it doesn't exist.
        """
        conn = sqlite3.connect(self._sqfile)
        cursor = conn.cursor()
        print(f"Writing sqlite file table: {self._sqfile}")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                created TEXT,
                name TEXT,
                level TEXT,
                message TEXT,
                hostname TEXT,
                process TEXT,
                thread TEXT
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

    def emit(self, record):
        """Emit a log record, and insert it into the database."""
        try:
            conn = sqlite3.connect(self._sqfile)
            cursor = conn.cursor()
            print("Dequeued item:", record)
            cursor.execute(
                "\n"
                "INSERT INTO logs "
                "(created, name, level, message, hostname, process, thread)\n"
                "VALUES (?, ?, ?, ?, ?, ?, ?)\n",
                (
                    datetime.datetime.fromtimestamp(record.created).strftime(DATEFMT),
                    record.name,
                    record.levelname,
                    record.getMessage(),
                    record.hostname,
                    record.process,
                    record.thread,
                ),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")

    def close(self):
        """Ensure the database connection is closed cleanly."""
        super().close()


class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record):
        if not hasattr(record, "elapsed"):
            record.elapsed = 0  # Default value if not provided
        if not hasattr(record, "memory"):
            record.memory = 0  # Default value if not provided

        # Call the base class's format method to handle the normal log formatting
        return super().format(record)


def start_logging_server(
    sqlite_filepath: str = None,
    host: str = "localhost",
    port: int = logging.handlers.DEFAULT_TCP_LOGGING_PORT,
):
    """
    Start the logging server.

    SIGINT (Ctrl-C) and SIGTERM drain pending connections and complete records
    already available on their sockets, without waiting for clients to send
    more data or disconnect. Records still missing bytes when no more data is
    available are discarded. In-progress record handling, including SQLite
    writes, finishes before the SQLite handler is closed and detached.
    Must run in the main thread.

    Request handlers are server-side threads receiving records from clients,
    which normally run in separate processes. Shutdown closes the server's
    connections; it does not close client-side SocketHandlers or stop client
    processes. Only the SQLite handler created here is detached and closed.
    The function then returns rather than explicitly exiting Python, so other
    handlers and threads in this process are not stopped by this function.

    Args:
    - `sqlite_filepath`: The file path to the SQLite database.  Optional.
    - `host`: The host name of the server.  Optional.
    - `port`: The port number the server is listening on.  Optional.

    """
    logging.basicConfig(
        format=(
            "%(relativeCreated)5d %(name)-15s %(levelname)-8s %(hostname)s "
            "%(process)d %(asctime)s %(message)s"
        ),
        datefmt=DATEFMT,
    )

    sqlite_handler = None
    original_signal_handlers = {}
    try:
        with LogRecordSocketReceiver(host=host, port=port) as tcpserver:

            def stop_server(signum, frame):
                tcpserver.abort = 1

            for signum in (signal.SIGINT, signal.SIGTERM):
                original_signal_handlers[signum] = signal.signal(signum, stop_server)

            if sqlite_filepath:
                sqlite_handler = SQLiteHandler(sqlite_filepath)
                logging.getLogger("").addHandler(sqlite_handler)
            bound_port = tcpserver.server_address[1]
            sqlite_info = (
                f"; SQLITE: {sqlite_filepath}" if sqlite_handler is not None else ""
            )
            print(
                "About to start TCP server...\n"
                f"HOST: {host}; PORT: {bound_port}; PID: {os.getpid()}{sqlite_info}\n"
                f"LOG_SERVER_READY port={bound_port}\n",
                flush=True,
            )
            try:
                tcpserver.serve_until_stopped()
            finally:
                tcpserver.abort = 1
    finally:
        try:
            if sqlite_handler is not None:
                logging.getLogger("").removeHandler(sqlite_handler)
                sqlite_handler.close()
        finally:
            for signum, handler in original_signal_handlers.items():
                signal.signal(signum, handler)


def main():
    """
    Entry point of the program.

    Parses command line arguments and executes the logging server
    """
    args, kwargs = function_to_argparse_parse_args(start_logging_server)
    start_logging_server(**args, **kwargs)


if __name__ == "__main__":
    main()
