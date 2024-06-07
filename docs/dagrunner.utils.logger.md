# module: `dagrunner.utils.logger`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L0)

This module takes much from the Python logging cookbook:
https://docs.python.org/3/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

- `client_attach_socket_handler`, a function that attaches a socket handler to the root
  logger.
- `ServerContext`, a context manager that starts and manages the TCP server on its own
  thread to receive log records.

## class: `LogRecordSocketReceiver`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L101)

### Call Signature:

```python
LogRecordSocketReceiver(host='localhost', port=9020, <class LogRecordStreamHandler>, log_queue=None)
```

Simple TCP socket-based logging receiver.

Specialisation of the `socketserver.ThreadingTCPServer` class to handle
log records.

### function: `__init__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L111)

#### Call Signature:

```python
__init__(self, host='localhost', port=9020, <class LogRecordStreamHandler>, log_queue=None)
```

Constructor.  May be extended, do not override.

### function: `serve_until_stopped`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L124)

#### Call Signature:

```python
serve_until_stopped(self, queue_handler=None)
```

### function: `stop`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L136)

#### Call Signature:

```python
stop(self)
```

## class: `LogRecordStreamHandler`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L52)

### Call Signature:

```python
LogRecordStreamHandler(request, client_address, server)
```

Handler for a streaming logging request.

Specialisation of the `socketserver.StreamRequestHandler` class to handle log
records and customise logging events.

### function: `handle`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L60)

#### Call Signature:

```python
handle(self)
```

Handle multiple requests - each expected to be a 4-byte length,
followed by the LogRecord in pickle format. Logs the record
according to whatever policy is configured locally.

### function: `handle_log_record`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L86)

#### Call Signature:

```python
handle_log_record(self, record)
```

### function: `unpickle`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L83)

#### Call Signature:

```python
unpickle(self, data)
```

## class: `SQLiteQueueHandler`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L141)

### Call Signature:

```python
SQLiteQueueHandler(sqfile='logs.sqlite')
```

### function: `__init__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L142)

#### Call Signature:

```python
__init__(self, sqfile='logs.sqlite')
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `close`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L190)

#### Call Signature:

```python
close(self)
```

### function: `write`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L167)

#### Call Signature:

```python
write(self, log_queue)
```

## class: `ServerContext`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L195)

### Call Signature:

```python
ServerContext(sqlite_filepath=None)
```

Start a TCP server to receive log records.

First run the server, and then the client. On the client side, nothing is printed
on the console; on the server side, you should see log messages printed to the
console.  The TC server is run in a separate thread enabling the main thread to
continue running other tasks.

Log format is:
%(relativeCreated)5d %(name)-15s %(levelname)-8s %(hostname)s %(process)d %(asctime)s %(message)s

### function: `__enter__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L214)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L236)

#### Call Signature:

```python
__exit__(self, exc_type, exc_val, exc_tb)
```

### function: `__init__`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L209)

#### Call Signature:

```python
__init__(self, sqlite_filepath=None)
```

Initialize self.  See help(type(self)) for accurate signature.

## function: `client_attach_socket_handler`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L24)

### Call Signature:

```python
client_attach_socket_handler()
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

## function: `main`

[Source](../../../../../../opt/hostedtoolcache/Python/3.9.19/x64/lib/python3.9/site-packages/dagrunner/utils/logger.py#L241)

### Call Signature:

```python
main()
```

Demonstrate how to start a TCP server to receive log records.

