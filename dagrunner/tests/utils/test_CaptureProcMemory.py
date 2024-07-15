# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import time
from unittest.mock import mock_open, patch

from dagrunner.utils import CaptureProcMemory

# this is what each open call will return
READ_DATA_LIST = [
    """VmPeak:	  1024 kB
VmSize:	  6144 kB
VmHWM:	    3072 kB
VmRSS:	    8192 kB
""",
    """VmPeak:	  5120 kB
VmSize:	  2048 kB
VmHWM:	    7168 kB
VmRSS:	    4096 kB
""",
]


def test_all():
    with patch("builtins.open", mock_open(read_data=READ_DATA_LIST[0])):
        with CaptureProcMemory(interval=0.01) as mem:
            time.sleep(0.02)
            with patch("builtins.open", mock_open(read_data=READ_DATA_LIST[1])):
                time.sleep(0.02)
    tar = {"VmPeak": 5.0, "VmSize": 6.0, "VmHWM": 7.0, "VmRSS": 8.0}
    assert mem.max() == tar
