# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from unittest.mock import mock_open, patch

from dagrunner.utils import get_sys_mem_stat

sys_status = """MemTotal:        7989852 kB
MemFree:          688700 kB
MemAvailable:    1684112 kB
Buffers:               0 kB
Cached:          1526676 kB
SwapCached:        19880 kB
Active:          4136476 kB
Inactive:        2345780 kB
Active(anon):    3494656 kB
Inactive(anon):  1706028 kB
Active(file):     641820 kB
Inactive(file):   639752 kB
"""


@patch("builtins.open", mock_open(read_data=sys_status))
def test_all():
    res = get_sys_mem_stat()
    tar = {
        "MemTotal": 7802.58984375,
        "MemFree": 672.55859375,
        "Buffers": 0.0,
        "Cached": 1490.89453125,
    }
    assert res == tar
