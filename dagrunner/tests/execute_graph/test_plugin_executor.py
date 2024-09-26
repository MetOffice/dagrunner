# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from unittest import mock

import pytest

from dagrunner.execute_graph import plugin_executor


class DummyPlugin:
    def __init__(self, init_named_arg, init_named_kwarg=None, **init_kwargs) -> None:
        self._init_named_arg = init_named_arg
        self._init_named_kwarg = init_named_kwarg
        self._init_kwargs = init_kwargs

    def __call__(
        self, *call_args, call_named_arg, call_named_kwarg=None, **call_kwargs
    ):
        return (
            f"init_kwargs={self._init_kwargs}; "
            f"init_named_arg={self._init_named_arg}; "
            f"init_named_kwarg={self._init_named_kwarg}; "
            f"call_args={call_args}; call_kwargs={call_kwargs}; "
            f"call_named_arg={call_named_arg}; call_named_kwarg={call_named_kwarg}; "
        )


class DummyPluginNoNamedParam:
    def __init__(self, **init_kwargs) -> None:
        self._init_kwargs = init_kwargs

    def __call__(self, *call_args, **call_kwargs):
        return (
            f"init_kwargs={self._init_kwargs}; "
            f"call_args={call_args}; call_kwargs={call_kwargs}; "
        )


@pytest.mark.parametrize(
    "plugin, init_args, call_args, target",
    [
        # Passing class init and call args
        (
            DummyPlugin,
            {
                "init_named_arg": mock.sentinel.init_named_arg,
                "init_named_kwarg": mock.sentinel.init_named_kwarg,
                "init_other_kwarg": mock.sentinel.init_other_kwarg,
            },
            {
                "call_named_arg": mock.sentinel.call_named_arg,
                "call_named_kwarg": mock.sentinel.call_named_kwarg,
                "call_other_kwarg": mock.sentinel.call_other_kwarg,
            },
            (
                "init_kwargs={'init_other_kwarg': sentinel.init_other_kwarg}; "
                "init_named_arg=sentinel.init_named_arg; "
                "init_named_kwarg=sentinel.init_named_kwarg; "
                "call_args=(sentinel.arg1, sentinel.arg2); "
                "call_kwargs={'call_other_kwarg': sentinel.call_other_kwarg}; "
                "call_named_arg=sentinel.call_named_arg; "
                "call_named_kwarg=sentinel.call_named_kwarg; "
            ),
        ),
        # Passing class init args only
        (
            DummyPluginNoNamedParam,
            {"init_other_kwarg": mock.sentinel.init_other_kwarg},
            None,
            (
                "init_kwargs={'init_other_kwarg': sentinel.init_other_kwarg}; "
                "call_args=(sentinel.arg1, sentinel.arg2); "
                "call_kwargs={}; "
            ),
        ),
        # Passing class call args only
        (
            DummyPluginNoNamedParam,
            None,
            {"call_other_kwarg": mock.sentinel.call_other_kwarg},
            (
                "init_kwargs={}; "
                "call_args=(sentinel.arg1, sentinel.arg2); "
                "call_kwargs={'call_other_kwarg': sentinel.call_other_kwarg}; "
            ),
        ),
    ],
)
def test_pass_class_arg_kwargs(plugin, init_args, call_args, target):
    """
    Test passing named parameters to plugin class initialisation and __call__
    method.
    """
    args = (mock.sentinel.arg1, mock.sentinel.arg2)
    call = tuple([plugin, init_args, call_args])
    res = plugin_executor(*args, call=call)
    assert res == target


def test_pass_common_args():
    """
    Passing 'common args', some relevant to class init and some to call method.
    """
    args = (mock.sentinel.arg1, mock.sentinel.arg2)
    common_kwargs = {
        "init_named_arg": mock.sentinel.init_named_arg,
        "init_named_kwarg": mock.sentinel.init_named_kwarg,
        # this should be ignored (as not part of class signature)
        "other_kwargs": mock.sentinel.other_kwargs,
        "call_named_arg": mock.sentinel.call_named_arg,
        "call_named_kwarg": mock.sentinel.call_named_kwarg,
    }
    target = (
        "init_kwargs={}; "
        "init_named_arg=sentinel.init_named_arg; "
        "init_named_kwarg=sentinel.init_named_kwarg; "
        "call_args=(sentinel.arg1, sentinel.arg2); "
        "call_kwargs={}; "
        "call_named_arg=sentinel.call_named_arg; "
        "call_named_kwarg=sentinel.call_named_kwarg; "
    )

    call = tuple([DummyPlugin, {}, {}])
    res = plugin_executor(*args, call=call, common_kwargs=common_kwargs)
    assert res == target


def test_pass_common_args_override():
    """Passing 'common args', some relevant to class init and some to call method."""
    args = (mock.sentinel.arg1, mock.sentinel.arg2)
    common_kwargs = {
        "init_named_arg": mock.sentinel.init_named_arg_override,
        "init_named_kwarg": mock.sentinel.init_named_kwarg_override,
        "call_named_arg": mock.sentinel.call_named_arg_override,
        "call_named_kwarg": mock.sentinel.call_named_kwarg_override,
    }
    call = tuple(
        [
            DummyPlugin,
            {
                "init_named_arg": mock.sentinel.init_named_arg,
                "init_named_kwarg": mock.sentinel.init_named_kwarg,
            },
            {
                "call_named_arg": mock.sentinel.call_named_arg,
                "call_named_kwarg": mock.sentinel.call_named_kwarg,
            },
        ]
    )
    target = (
        "init_kwargs={}; "
        "init_named_arg=sentinel.init_named_arg_override; "
        "init_named_kwarg=sentinel.init_named_kwarg_override; "
        "call_args=(sentinel.arg1, sentinel.arg2); "
        "call_kwargs={}; "
        "call_named_arg=sentinel.call_named_arg_override; "
        "call_named_kwarg=sentinel.call_named_kwarg_override; "
    )
    res = plugin_executor(*args, call=call, common_kwargs=common_kwargs)
    assert res == target
