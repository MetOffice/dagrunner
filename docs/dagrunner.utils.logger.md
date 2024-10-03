# module: `dagrunner.utils.logger`

[Source](../dagrunner/utils/logger.py#L0)

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

see [function: dagrunner.utils.function_to_argparse_parse_args](dagrunner.utils.md#function-function_to_argparse_parse_args)

## class: `CustomFormatter`

[Source](../dagrunner/utils/logger.py#L217)

### Call Signature:

```python
CustomFormatter(fmt=None, datefmt=None)
```

Formatter instances are used to convert a LogRecord to text.

Formatters need to know how a LogRecord is constructed. They are
responsible for converting a LogRecord to (usually) a string which can
be interpreted by either a human or an external system. The base Formatter
allows a formatting string to be specified. If none is supplied, the
style-dependent default value, "%(message)s", "{message}", or
"${message}", is used.

The Formatter can be initialized with a format string which makes use of
knowledge of the LogRecord attributes - e.g. the default value mentioned
above makes use of the fact that the user's message and arguments are pre-
formatted into a LogRecord's message attribute. Currently, the useful
attributes in a LogRecord are described by:

%(name)s            Name of the logger (logging channel)
%(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                    WARNING, ERROR, CRITICAL)
%(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                    "WARNING", "ERROR", "CRITICAL")
%(pathname)s        Full pathname of the source file where the logging
                    call was issued (if available)
%(filename)s        Filename portion of pathname
%(module)s          Module (name portion of filename)
%(lineno)d          Source line number where the logging call was issued
                    (if available)
%(funcName)s        Function name
%(created)f         Time when the LogRecord was created (time.time()
                    return value)
%(asctime)s         Textual time when the LogRecord was created
%(msecs)d           Millisecond portion of the creation time
%(relativeCreated)d Time in milliseconds when the LogRecord was created,
                    relative to the time the logging module was loaded
                    (typically at application startup time)
%(thread)d          Thread ID (if available)
%(threadName)s      Thread name (if available)
%(taskName)s        Task name (if available)
%(process)d         Process ID (if available)
%(message)s         The result of record.getMessage(), computed just as
                    the record is emitted

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L218)

#### Call Signature:

```python
__init__(self, fmt=None, datefmt=None)
```

Initialize the formatter with specified format strings.

Initialize the formatter either with the specified format string, or a
default as described above. Allow for specialized date formatting with
the optional datefmt argument. If datefmt is omitted, you get an
ISO8601-like (or RFC 3339-like) format.

Use a style parameter of '%', '{' or '$' to specify that you want to
use one of %-formatting, :meth:`str.format` (``{}``) formatting or
:class:`string.Template` formatting in your format string.

.. versionchanged:: 3.2
   Added the ``style`` parameter.

### function: `format`

[Source](../dagrunner/utils/logger.py#L221)

#### Call Signature:

```python
format(self, record)
```

Format the specified record as text.

The record's attribute dictionary is used as the operand to a
string formatting operation which yields the returned string.
Before formatting the dictionary, a couple of preparatory steps
are carried out. The message attribute of the record is computed
using LogRecord.getMessage(). If the formatting string uses the
time (as determined by a call to usesTime(), formatTime() is
called to format the event time. If there is exception information,
it is formatted using formatException() and appended to the message.

## str: `DATEFMT`

## class: `LogRecordSocketReceiver`

[Source](../dagrunner/utils/logger.py#L121)

### Call Signature:

```python
LogRecordSocketReceiver(host='localhost', port=9020, <class LogRecordStreamHandler>)
```

Simple TCP socket-based logging receiver.

Specialisation of the `socketserver.ThreadingTCPServer` class to handle
log records.

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L131)

#### Call Signature:

```python
__init__(self, host='localhost', port=9020, <class LogRecordStreamHandler>)
```

Constructor.  May be extended, do not override.

### function: `serve_until_stopped`

[Source](../dagrunner/utils/logger.py#L142)

#### Call Signature:

```python
serve_until_stopped(self)
```

## class: `LogRecordStreamHandler`

[Source](../dagrunner/utils/logger.py#L76)

### Call Signature:

```python
LogRecordStreamHandler(request, client_address, server)
```

Handler for a streaming logging request.

Specialisation of the `socketserver.StreamRequestHandler` class to handle log
records and customise logging events.

### function: `handle`

[Source](../dagrunner/utils/logger.py#L84)

#### Call Signature:

```python
handle(self)
```

Handle multiple requests - each expected to be a 4-byte length,
followed by the LogRecord in pickle format. Logs the record
according to whatever policy is configured locally.

### function: `handle_log_record`

[Source](../dagrunner/utils/logger.py#L106)

#### Call Signature:

```python
handle_log_record(self, record)
```

### function: `unpickle`

[Source](../dagrunner/utils/logger.py#L103)

#### Call Signature:

```python
unpickle(self, data)
```

## class: `SQLiteHandler`

[Source](../dagrunner/utils/logger.py#L153)

### Call Signature:

```python
SQLiteHandler(sqfile='logs.sqlite')
```

Custom logging handler to write log messages to an SQLite database.

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L158)

#### Call Signature:

```python
__init__(self, sqfile='logs.sqlite')
```

Initializes the instance - basically setting the formatter to None
and the filter list to empty.

### function: `close`

[Source](../dagrunner/utils/logger.py#L212)

#### Call Signature:

```python
close(self)
```

Ensure the database connection is closed cleanly.

### function: `emit`

[Source](../dagrunner/utils/logger.py#L185)

#### Call Signature:

```python
emit(self, record)
```

Emit a log record, and insert it into the database.

## function: `client_attach_socket_handler`

[Source](../dagrunner/utils/logger.py#L43)

### Call Signature:

```python
client_attach_socket_handler(host: str = 'localhost', port: int = 9020)
```

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

## function: `main`

[Source](../dagrunner/utils/logger.py#L265)

### Call Signature:

```python
main()
```

Entry point of the program.

Parses command line arguments and executes the logging server

## function: `start_logging_server`

[Source](../dagrunner/utils/logger.py#L231)

### Call Signature:

```python
start_logging_server(sqlite_filepath: str = None, host: str = 'localhost', port: int = 9020, verbose: bool = False)
```

Start the logging server.

Args:
- `sqlite_filepath`: The file path to the SQLite database.  Optional.
- `host`: The host name of the server.  Optional.
- `port`: The port number the server is listening on.  Optional.
- `verbose`: Whether to print verbose output.  Optional.

