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
import socket
import socketserver
import sqlite3
import struct

from dagrunner.utils import function_to_argparse_parse_args

__all__ = ["client_attach_socket_handler", "start_logging_server"]


DATEFMT = "%Y-%m-%dT%H:%M:%S"  # Date in ISO 8601 format


def client_attach_socket_handler(
    host: str = "localhost", port: int = logging.handlers.DEFAULT_TCP_LOGGING_PORT
):
    """
    Attach a SocketHandler instance to the root logger at the sending end.

    Now, we can log to the root logger, or any other logger. First the root...
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

    """
    rootLogger = logging.getLogger("")
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

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
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
        import select

        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


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
    verbose: bool = False,
):
    """
    Start the logging server.

    Args:
    - `sqlite_filepath`: The file path to the SQLite database.  Optional.
    - `host`: The host name of the server.  Optional.
    - `port`: The port number the server is listening on.  Optional.
    - `verbose`: Whether to print verbose output.  Optional.
    """
    logging.basicConfig(
        format=(
            "%(relativeCreated)5d %(name)-15s %(levelname)-8s %(hostname)s "
            "%(process)d %(asctime)s %(message)s"
        ),
        datefmt=DATEFMT,
    )

    tcpserver = LogRecordSocketReceiver(host=host, port=port)
    if sqlite_filepath:
        sqlite_handler = SQLiteHandler(sqlite_filepath)
        logging.getLogger("").addHandler(sqlite_handler)
    print(
        "About to start TCP server...\n",
        f"HOST: {host}; PORT: {port}; PID: {os.getpid()}; SQLITE: {sqlite_filepath}\n",
    )
    tcpserver.serve_until_stopped()


def main():
    """
    Entry point of the program.

    Parses command line arguments and executes the logging server
    """
    args, kwargs = function_to_argparse_parse_args(start_logging_server)
    start_logging_server(**args, **kwargs)()


if __name__ == "__main__":
    main()
