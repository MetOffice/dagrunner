# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import os

import pytest

from dagrunner.execute_graph import get_object_path


def test_func(): ...


class TestClass: ...


TEST_INSTANCE = TestClass()
TEST_LAMBDA = lambda: None
TEST_STRING = os.path.abspath(__file__)

TEST_CASES = [test_func, TestClass, TEST_INSTANCE, TEST_LAMBDA, TEST_STRING]


@pytest.mark.parametrize("test_object", TEST_CASES)
def test_get_object_path(test_object):
    """Test get_object_path with parametrized range of objects."""
    assert os.path.abspath(__file__) == get_object_path(test_object)
