"""
This module takes much from the Python logging cookbook:
https://docs.python.org/3/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

- client_attach_socket_handler, a function that attaches a socket handler to the root
  logger.
- ServerContext, a context manager that starts and manages the TCP server on its own
  thread to receive log records.
"""
import logging, logging.handlers
import pickle
import socket
import socketserver
import struct
import threading
import queue


__all__ = ['client_attach_socket_handler', 'ServerContext']


def client_attach_socket_handler():
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
    """
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler('localhost',
                        logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    # don't bother with a formatter, since a socket handler sends the event as
    # an unformatted pickle
    rootLogger.addHandler(socketHandler)


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """
    Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
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
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            # Modify record to include hostname
            record.hostname = socket.gethostname()
            self.handleLogRecord(record)

            # Push log record to the queue for database writing
            self.server.log_queue.put(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
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
    """

    allow_reuse_address = True

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler, log_queue=None):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None
        self.log_queue = log_queue  # Store the reference to the log queue

    def serve_until_stopped(self, queue_handler=None):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
                queue_handler.write(self.log_queue)
            abort = self.abort
        queue_handler.close()

    def stop(self):
        self.server_close()  # Close the server socket
        self.abort = 1  # Set abort flag to stop the server loop


class SQLiteQueueHandler:
    def __init__(self, sqfile='logs.sqlite'):
        self._sqfile = sqfile
        self._conn = None

    @property
    def db(self):
        if self._conn is None:
            import sqlite3
            self._conn = sqlite3.connect(self._sqfile)  # Connect to the SQLite database
            cursor = self._conn.cursor()
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
            """)  # Create the 'logs' table if it doesn't exist
        return self._conn

    def write(self, log_queue):
        while not log_queue.empty():
            record = log_queue.get()
            print("Dequeued item:", record)
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO logs (created, name, level, message, hostname, process, thread)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (record.created, record.name, record.levelname, record.getMessage(), record.hostname, record.process, record.thread))
            self.db.commit()  # Commit the transaction
        
    def close(self):
        if self._conn:
            self._conn.close()


class ServerContext:
    """
    Start a TCP server to receive log records.

    First run the server, and then the client. On the client side, nothing is printed
    on the console; on the server side, you should see log messages printed to the
    console.  The TC server is run in a separate thread enabling the main thread to
    continue running other tasks.

    Log format is:
    %(relativeCreated)5d %(name)-15s %(levelname)-8s %(hostname)s %(process)d %(asctime)s %(message)s

    """
    def __init__(self, sqlite_filepath=None):
        self.tcpserver = None
        self.server_thread = None

    def __enter__(self):
        logging.basicConfig(
            format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(hostname)s %(process)d %(asctime)s %(message)s',
            datefmt="%Y-%m-%dT%H:%M:%S")  # Date in ISO 8601 format
        
        self.log_queue = queue.Queue()

        sqlitequeue = None
        if sqlite_filepath:
            sqlitequeue = SQLiteQueueHandler(sqfile=sqlite_filepath)

        self.tcpserver = LogRecordSocketReceiver(log_queue=self.log_queue)
        print('About to start TCP server...')
        self.server_thread = threading.Thread(target=self.tcpserver.serve_until_stopped, kwargs={'queue_handler': sqlitequeue})
        self.server_thread.start()

        return self.server_thread, self.tcpserver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tcpserver.stop()
        self.server_thread.join()


def main():
    """
    Demonstrate how to start a TCP server to receive log records.
    """
    with ServerContext():
        print("Doing something while the server is running")
        input("Press Enter to stop the server...")
    print("Server stopped")


if __name__ == '__main__':
    main()