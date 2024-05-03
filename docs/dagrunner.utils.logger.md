# module: `dagrunner.utils.logger`

[Source](../dagrunner/utils/logger.py#L0)

This module takes much from the Python logging cookbook:
https://docs.python.org/3/howto/logging-cookbook.html#sending-and-receiving-logging-events-across-a-network

- client_attach_socket_handler, a function that attaches a socket handler to the root
  logger.
- ServerContext, a context manager that starts and manages the TCP server on its own
  thread to receive log records.

## class: `LogRecordSocketReceiver`

[Source](../dagrunner/utils/logger.py#L98)

### Call Signature:

```python
LogRecordSocketReceiver(host='localhost', port=9020, <class LogRecordStreamHandler>, log_queue=None)
```

Simple TCP socket-based logging receiver.

### function: `__enter__`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L383)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L386)

#### Call Signature:

```python
__exit__(self, *args)
```

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L105)

#### Call Signature:

```python
__init__(self, host='localhost', port=9020, <class LogRecordStreamHandler>, log_queue=None)
```

Constructor.  May be extended, do not override.

### function: `close_request`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L511)

#### Call Signature:

```python
close_request(self, request)
```

Called to clean up an individual request.

### function: `fileno`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L485)

#### Call Signature:

```python
fileno(self)
```

Return socket file number.

Interface required by selector.

### function: `finish_request`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L358)

#### Call Signature:

```python
finish_request(self, request, client_address)
```

Finish one request by instantiating RequestHandlerClass.

### function: `get_request`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L493)

#### Call Signature:

```python
get_request(self)
```

Get the request and client address from the socket.

May be overridden.

### function: `handle_error`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L370)

#### Call Signature:

```python
handle_error(self, request, client_address)
```

Handle an error gracefully.  May be overridden.

The default is to print a traceback and continue.

### function: `handle_request`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L273)

#### Call Signature:

```python
handle_request(self)
```

Handle one request, possibly blocking.

Respects self.timeout.

### function: `handle_timeout`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L326)

#### Call Signature:

```python
handle_timeout(self)
```

Called if no new request arrives within self.timeout.

Overridden by ForkingMixIn.

### function: `process_request`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L689)

#### Call Signature:

```python
process_request(self, request, client_address)
```

Start a new thread to process the request.

### function: `process_request_thread`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L676)

#### Call Signature:

```python
process_request_thread(self, request, client_address)
```

Same as in BaseServer but as a thread.

In addition, exception handling is done here.

### function: `serve_forever`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L215)

#### Call Signature:

```python
serve_forever(self, poll_interval=0.5)
```

Handle one request at a time until shutdown.

Polls for shutdown every poll_interval seconds. Ignores
self.timeout. If you need to do periodic tasks, do them in
another thread.

### function: `serve_until_stopped`

[Source](../dagrunner/utils/logger.py#L114)

#### Call Signature:

```python
serve_until_stopped(self, queue_handler=None)
```

### function: `server_activate`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L469)

#### Call Signature:

```python
server_activate(self)
```

Called by constructor to activate the server.

May be overridden.

### function: `server_bind`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L458)

#### Call Signature:

```python
server_bind(self)
```

Called by constructor to bind the socket.

May be overridden.

### function: `server_close`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L699)

#### Call Signature:

```python
server_close(self)
```

### function: `service_actions`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L254)

#### Call Signature:

```python
service_actions(self)
```

Called by the serve_forever() loop.

May be overridden by a subclass / Mixin to implement any code that
needs to be run during the loop.

### function: `shutdown`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L244)

#### Call Signature:

```python
shutdown(self)
```

Stops the serve_forever loop.

Blocks until the loop has finished. This must be called while
serve_forever() is running in another thread, or it will
deadlock.

### function: `shutdown_request`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L501)

#### Call Signature:

```python
shutdown_request(self, request)
```

Called to shutdown and close an individual request.

### function: `stop`

[Source](../dagrunner/utils/logger.py#L127)

#### Call Signature:

```python
stop(self)
```

### function: `verify_request`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L333)

#### Call Signature:

```python
verify_request(self, request, client_address)
```

Verify the request.  May be overridden.

Return True if we should proceed with this request.

## class: `LogRecordStreamHandler`

[Source](../dagrunner/utils/logger.py#L49)

### Call Signature:

```python
LogRecordStreamHandler(request, client_address, server)
```

Handler for a streaming logging request.

This basically logs the record using whatever logging policy is
configured locally.

### function: `__init__`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L741)

#### Call Signature:

```python
__init__(self, request, client_address, server)
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `finish`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L803)

#### Call Signature:

```python
finish(self)
```

### function: `handle`

[Source](../dagrunner/utils/logger.py#L57)

#### Call Signature:

```python
handle(self)
```

Handle multiple requests - each expected to be a 4-byte length,
followed by the LogRecord in pickle format. Logs the record
according to whatever policy is configured locally.

### function: `handle_log_record`

[Source](../dagrunner/utils/logger.py#L83)

#### Call Signature:

```python
handle_log_record(self, record)
```

### function: `setup`

[Source](../../../../../../project/ukmo/scitools/opt_scitools/conda/deployments/default-2023_11_28/lib/python3.10/socketserver.py#L790)

#### Call Signature:

```python
setup(self)
```

### function: `unpickle`

[Source](../dagrunner/utils/logger.py#L80)

#### Call Signature:

```python
unpickle(self, data)
```

## class: `SQLiteQueueHandler`

[Source](../dagrunner/utils/logger.py#L132)

### Call Signature:

```python
SQLiteQueueHandler(sqfile='logs.sqlite')
```

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L133)

#### Call Signature:

```python
__init__(self, sqfile='logs.sqlite')
```

Initialize self.  See help(type(self)) for accurate signature.

### function: `close`

[Source](../dagrunner/utils/logger.py#L169)

#### Call Signature:

```python
close(self)
```

### function: `write`

[Source](../dagrunner/utils/logger.py#L157)

#### Call Signature:

```python
write(self, log_queue)
```

## class: `ServerContext`

[Source](../dagrunner/utils/logger.py#L174)

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

[Source](../dagrunner/utils/logger.py#L192)

#### Call Signature:

```python
__enter__(self)
```

### function: `__exit__`

[Source](../dagrunner/utils/logger.py#L210)

#### Call Signature:

```python
__exit__(self, exc_type, exc_val, exc_tb)
```

### function: `__init__`

[Source](../dagrunner/utils/logger.py#L187)

#### Call Signature:

```python
__init__(self, sqlite_filepath=None)
```

Initialize self.  See help(type(self)) for accurate signature.

## function: `client_attach_socket_handler`

[Source](../dagrunner/utils/logger.py#L22)

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

[Source](../dagrunner/utils/logger.py#L215)

### Call Signature:

```python
main()
```

Demonstrate how to start a TCP server to receive log records.

