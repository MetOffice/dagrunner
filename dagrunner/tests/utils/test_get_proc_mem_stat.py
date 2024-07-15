# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from unittest.mock import mock_open, patch

from dagrunner.utils import get_proc_mem_stat

proc_status = """Name:	bash
Umask:	0022
State:	S (sleeping)
Tgid:	95395
Ngid:	0
Pid:	95395
PPid:	81896
TracerPid:	0
Uid:	10234	10234	10234	10234
Gid:	1000	1000	1000	1000
FDSize:	256
Groups:	39 203 216 1000 1460 6790 11250
VmPeak:	  130448 kB
VmSize:	  130448 kB
VmLck:	       0 kB
VmPin:	       0 kB
VmHWM:	    4384 kB
VmRSS:	    3108 kB
RssAnon:	    2632 kB
RssFile:	     476 kB
RssShmem:	       0 kB
VmData:	    2496 kB
VmStk:	     144 kB
VmExe:	     888 kB
VmLib:	    2188 kB
VmPTE:	      76 kB
VmSwap:	       0 kB
Threads:	1
"""


@patch("builtins.open", mock_open(read_data=proc_status))
def test_all():
    res = get_proc_mem_stat()
    tar = {
        "VmPeak": 127.390625,
        "VmSize": 127.390625,
        "VmHWM": 4.28125,
        "VmRSS": 3.03515625,
    }
    assert res == tar
