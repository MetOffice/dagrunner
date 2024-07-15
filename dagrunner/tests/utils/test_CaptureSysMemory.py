# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import time
from unittest.mock import mock_open, patch

from dagrunner.utils import CaptureSysMemory

# this is what each open call will return
READ_DATA_LIST = [
    """Committed_AS:	  1024 kB
MemFree:	  6144 kB
Buffers:	    3072 kB
Cached:	    8192 kB
MemTotal:    1024 kB
""",
    """Committed_AS:	  5120 kB
MemFree:	  2048 kB
Buffers:	    7168 kB
Cached:	    4096 kB
MemTotal:    2048 kB
""",
]


def test_all():
    with patch("builtins.open", mock_open(read_data=READ_DATA_LIST[0])):
        with CaptureSysMemory(interval=0.01) as mem:
            time.sleep(0.02)
            with patch("builtins.open", mock_open(read_data=READ_DATA_LIST[1])):
                time.sleep(0.02)
    tar = {
        "Committed_AS": 5.0,
        "MemFree": 6.0,
        "Buffers": 7.0,
        "Cached": 8.0,
        "MemTotal": 2.0,
    }
    assert mem.max() == tar
