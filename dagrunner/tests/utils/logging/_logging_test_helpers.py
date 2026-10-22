# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import os
import selectors
import time


def wait_for_logging_server_port(process, timeout=5):
    """Read the port reported after the subprocess has bound its socket."""
    output = bytearray()
    deadline = time.monotonic() + timeout
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise AssertionError(
                    "Logging server exited before becoming ready: "
                    f"{output.decode(errors='replace')}"
                )
            events = selector.select(min(0.1, deadline - time.monotonic()))
            for key, _ in events:
                chunk = os.read(key.fileobj.fileno(), 4096)
                if not chunk:
                    continue
                output.extend(chunk)
                for line in output.splitlines():
                    if line.startswith(b"LOG_SERVER_READY "):
                        _, port = line.decode().split("port=", 1)
                        return int(port)
    raise TimeoutError(
        "Logging server did not report its bound port: "
        f"{output.decode(errors='replace')}"
    )
