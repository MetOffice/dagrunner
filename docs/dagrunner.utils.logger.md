# module: `dagrunner.utils.logger`

[Source](../dagrunner/utils/logger.py#L0)

This module takes much from the Python logging cookbook:
https://docs.python.org/3/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

- client_attach_socket_handler, a function that attaches a socket handler to the root
  logger.
- ServerContext, a context manager that starts and manages the TCP server on its own
  thread to receive log records.

# class: `LogRecordSocketReceiver`

[Source](../dagrunner/utils/logger.py#L98)

Simple TCP socket-based logging receiver.

# class: `LogRecordStreamHandler`

[Source](../dagrunner/utils/logger.py#L49)

Handler for a streaming logging request.

This basically logs the record using whatever logging policy is
configured locally.

# class: `SQLiteQueueHandler`

[Source](../dagrunner/utils/logger.py#L132)

# class: `ServerContext`

[Source](../dagrunner/utils/logger.py#L174)

Start a TCP server to receive log records.

First run the server, and then the client. On the client side, nothing is printed
on the console; on the server side, you should see log messages printed to the
console.  The TC server is run in a separate thread enabling the main thread to
continue running other tasks.

Log format is:
%(relativeCreated)5d %(name)-15s %(levelname)-8s %(hostname)s %(process)d %(asctime)s %(message)s

# function: `client_attach_socket_handler`

[Source](../dagrunner/utils/logger.py#L22)

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

# function: `main`

[Source](../dagrunner/utils/logger.py#L215)

Demonstrate how to start a TCP server to receive log records.

