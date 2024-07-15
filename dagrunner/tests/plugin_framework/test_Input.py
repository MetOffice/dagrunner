# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import os

from dagrunner.plugin_framework import Input


def test_basic():
    input = Input()
    os.environ["SOME_ROOT"] = "/path/to/data"
    kwargs = {
        "current_cycle": "20210101T0000Z",
        "data_input_path": "input",
    }
    filepath = "$SOME_ROOT/{data_input_path}/{current_cycle}"
    res = input(filepath=filepath, **kwargs)
    assert res == "/path/to/data/input/20210101T0000Z"


def test_recursive():
    # Expand twice
    input = Input()
    kwargs = {
        "current_cycle": "20210101T0000Z",
        "data_input_path": "{current_cycle}",
    }
    filepath = "{data_input_path}"
    res = input(filepath=filepath, **kwargs)
    assert res == "20210101T0000Z"
