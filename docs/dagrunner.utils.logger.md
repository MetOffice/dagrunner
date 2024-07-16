# module: `dagrunner.utils.logger`

[Source](../dagrunner/utils/logger.py#L0)

This module takes much from the Python logging cookbook:
https://docs.python.org/3/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

## Overview

- `client_attach_socket_handler`, a function that attaches a socket handler
  `logging.handlers.SocketHandler` to the root logger with the specified host name and
  port number.
- `ServerContext`, a context manager that starts and manages the TCP server
  `LogRecordSocketReceiver` on its own thread, ready to receive log records.
  - `SQLiteQueueHandler`, which is managed by the server context and writes log records
    to an SQLite database.
  - `LogRecordSocketReceiver(socketserver.ThreadingTCPServer)`, the TCP server running
    on a specified host and port, managed by the server context that receives log
    records and utilises the `LogRecordStreamHandler` handler.
    - `LogRecordStreamHandler`, a specialisation of the
      `socketserver.StreamRequestHandler`, responsible for 'getting' log records.

## class: `LogRecordSocketReceiver`

[Source](../dagrunner/utils/logger.py#L119)

### Call Signature:

```python
LogRecordSocketReceiver(host='localhost', port=9020, <class LogRecordStreamHandler>, log_queue=None)
```

Simple TCP socket-based logging receiver.

Specialisation of the `socketserver.ThreadingTCPServer` class to handle
log records.

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L129)

#### Call Signature:

```python
__init__(self, host='localhost', port=9020, <class LogRecordStreamHandler>, log_queue=None)
```

Constructor.  May be extended, do not override.

### function: `serve_until_stopped`

[Source](../dagrunner/utils/logger.py#L142)

#### Call Signature:

```python
serve_until_stopped(self, queue_handler=None)
```

### function: `stop`

[Source](../dagrunner/utils/logger.py#L156)

#### Call Signature:

```python
stop(self)
```

## class: `LogRecordStreamHandler`

[Source](../dagrunner/utils/logger.py#L70)

### Call Signature:

```python
LogRecordStreamHandler(request, client_address, server)
```

Handler for a streaming logging request.

Specialisation of the `socketserver.StreamRequestHandler` class to handle log
records and customise logging events.

### function: `handle`

[Source](../dagrunner/utils/logger.py#L78)

#### Call Signature:

```python
handle(self)
```

Handle multiple requests - each expected to be a 4-byte length,
followed by the LogRecord in pickle format. Logs the record
according to whatever policy is configured locally.

### function: `handle_log_record`

[Source](../dagrunner/utils/logger.py#L104)

#### Call Signature:

```python
handle_log_record(self, record)
```

### function: `unpickle`

[Source](../dagrunner/utils/logger.py#L101)

#### Call Signature:

```python
unpickle(self, data)
```

## class: `SQLiteQueueHandler`

[Source](../dagrunner/utils/logger.py#L161)

### Call Signature:

```python
SQLiteQueueHandler(sqfile='logs.sqlite', verbose=False)
```

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L162)

#### Call Signature:

```python
__init__(self, sqfile='logs.sqlite', verbose=False)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `close`

[Source](../dagrunner/utils/logger.py#L214)

#### Call Signature:

```python
close(self)
```

### function: `write`

[Source](../dagrunner/utils/logger.py#L189)

#### Call Signature:

```python
write(self, log_queue)
```

## class: `ServerContext`

[Source](../dagrunner/utils/logger.py#L219)

### Call Signature:

```python
ServerContext(host: str = 'localhost', port: int = 9020, sqlite_filepath: str = None, verbose: bool = False)
```

Start a TCP server to receive log records.

First run the server, and then the client. On the client side, nothing is printed
on the console; on the server side, you should see log messages printed to the
console.  The TC server is run in a separate thread enabling the main thread to
continue running other tasks.

Log format is:
%(relativeCreated)5d %(name)-15s %(levelname)-8s %(hostname)s %(process)d
%(asctime)s %(message)s

Args:
- `host`: The host name of the server.  Optional.
- `port`: The port number the server is listening on.  Optional.
- `sqlite_filepath`: The path to the SQLite database file.  Don't write to a
  file if not provided.  Optional.
- `verbose`: Whether to print verbose output.  Optional.

### function: `__enter__`

[Source](../dagrunner/utils/logger.py#L255)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../dagrunner/utils/logger.py#L285)

#### Call Signature:

```python
__exit__(self, exc_type, exc_val, exc_tb)
```

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L241)

#### Call Signature:

```python
__init__(self, host: str = 'localhost', port: int = 9020, sqlite_filepath: str = None, verbose: bool = False)
```

Initialize self.  See help(type(self)) for accurate signature.

## function: `client_attach_socket_handler`

[Source](../dagrunner/utils/logger.py#L37)

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

[Source](../dagrunner/utils/logger.py#L290)

### Call Signature:

```python
main()
```

Demonstrate how to start a TCP server to receive log records.

