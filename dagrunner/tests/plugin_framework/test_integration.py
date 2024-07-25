# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from dagrunner.plugin_framework import LoadJson, LoadPickle, SaveJson, SavePickle


def test_json_roundtrip(tmp_path):
    testfile = tmp_path / "test.json"
    data = {"key": "value"}
    SaveJson()(data, filepath=testfile)
    res = LoadJson()(testfile)
    assert data == res


def test_pickle_roundtrip(tmp_path):
    testfile = tmp_path / "test.pickle"
    data = {"key": "value"}
    SavePickle()(data, filepath=testfile)
    res = LoadPickle()(testfile)
    assert data == res
