# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from unittest import mock

from dagrunner.execute_graph import plugin_executor


class DummyPlugin:
    def __init__(self, iarg1, ikwarg1=None) -> None:
        self._iarg1 = iarg1
        self._ikwarg1 = ikwarg1

    def __call__(self, *args, kwarg1=None, **kwargs):
        return f"iarg1={self._iarg1}; ikwarg1={self._ikwarg1}; args={args}; kwarg1={kwarg1}; kwargs={kwargs}"


def test_pass_class_arg_kwargs():
    """Test passing named parameters to plugin class and __call__ method."""
    args = (mock.sentinel.arg1, mock.sentinel.arg2)
    call = tuple(
        [
            DummyPlugin,
            {"iarg1": mock.sentinel.iarg1, "ikwarg1": mock.sentinel.ikwarg1},
            {"kwarg1": mock.sentinel.kwarg1},
        ]
    )
    res = plugin_executor(*args, call=call)
    assert (
        res
        == "iarg1=sentinel.iarg1; ikwarg1=sentinel.ikwarg1; args=(sentinel.arg1, sentinel.arg2); kwarg1=sentinel.kwarg1; kwargs={}"
    )


def test_pass_common_args():
    """Passing 'common args', some relevant to class init and some to call method."""
    args = (mock.sentinel.arg1, mock.sentinel.arg2)
    common_kwargs = {
        "ikwarg1": mock.sentinel.ikwarg1,
        "kwarg1": mock.sentinel.kwarg1,
        "iarg1": mock.sentinel.iarg1,
    }

    # call without common args (iarg1 is positional so non-optional)
    call = tuple([DummyPlugin, {"iarg1": mock.sentinel.iarg1}, {}])
    res = plugin_executor(*args, call=call)
    assert (
        res
        == "iarg1=sentinel.iarg1; ikwarg1=None; args=(sentinel.arg1, sentinel.arg2); kwarg1=None; kwargs={}"
    )

    # call with common args
    call = tuple([DummyPlugin, {}, {}])
    res = plugin_executor(*args, call=call, common_kwargs=common_kwargs)
    assert (
        res
        == "iarg1=sentinel.iarg1; ikwarg1=sentinel.ikwarg1; args=(sentinel.arg1, sentinel.arg2); kwarg1=sentinel.kwarg1; kwargs={}"
    )
