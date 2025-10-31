# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from unittest import mock

import pytest

from dagrunner.config import GlobalConfiguration
from dagrunner.events import IGNORE_EVENT, SKIP_EVENT
from dagrunner.execute_graph import plugin_executor


@pytest.fixture(autouse=True)
def patch_config():
    """Stop picking up any configuration from the environment."""
    with mock.patch("dagrunner.execute_graph.CONFIG", new=GlobalConfiguration()):
        yield


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


def test_ignore_event():
    """Check what happens a subset of arguments and all arguments are IGNORE_EVENT."""
    call = tuple([lambda x: x + 5])
    res = plugin_executor(*(5, IGNORE_EVENT), call=call)
    assert res == 10

    res = plugin_executor(*(IGNORE_EVENT, IGNORE_EVENT), call=call)
    assert res == IGNORE_EVENT


def test_skip_event():
    """Check what happens a subset of arguments are SKIP_EVENT."""
    call = tuple([lambda x: x + 5])
    res = plugin_executor(*(5, SKIP_EVENT), call=call)
    assert res == SKIP_EVENT


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


def test_missing_call_args():
    """Raise an error if 'call' arg isn't provided."""
    kwargs = {"key1": mock.sentinel.value1, "key2": mock.sentinel.value2}
    msg = f"call is a required argument\nnode_properties: {kwargs}"
    with pytest.raises(ValueError, match=msg):
        plugin_executor(mock.sentinel.arg1, **kwargs)


def test_class_plugin_unexpected_tuple_unpack():
    """Expecting inits kwargs and call kwargs but no more."""
    msg = "expecting 1, 2 or 3 values to unpack.*got 4"
    with pytest.raises(ValueError, match=msg):
        plugin_executor(mock.sentinel.arg1, call=(DummyPlugin, {}, {}, {}))


def test_callable_plugin_unexpected_tuple_unpack():
    """Expecting call kwargs but no more."""
    msg = "expecting 1 or 2 values to unpack.*got 3"
    with pytest.raises(ValueError, match=msg):
        plugin_executor(mock.sentinel.arg1, call=(DummyPluginNoNamedParam(), {}, {}))


class BadDummyInitPlugin:
    def __init__(self, **kwargs):
        raise ValueError("some error")

    def __call__(self, *args, **kwargs):
        pass


def test_extended_init_failure_context():
    with pytest.raises(RuntimeError, match="Failed to initialise"):
        plugin_executor(mock.sentinel.arg1, call=(BadDummyInitPlugin,))


def bad_call_plugin(*args):
    raise ValueError("some error")


def test_extended_call_plugin_failure_context():
    with pytest.raises(RuntimeError, match="Failed to execute"):
        plugin_executor(mock.sentinel.arg1, call=(bad_call_plugin,))


def test_non_hashable_args():
    """Test that non-hashable args (e.g. lists) are handled correctly."""

    class ListArgPlugin:
        def __init__(self, **kwargs):
            pass

        def __call__(self, list_arg):
            return [x * 2 for x in list_arg]

    call = (ListArgPlugin, {}, {})
    res = plugin_executor(*([1, 2, 3],), call=call)
    assert res == [2, 4, 6]


def test_cached_execution_disabled():
    """Test that execution works without cache utilisation."""
    args = (5,)

    mock_callable = mock.Mock(side_effect=lambda x: x + 5)
    call = tuple([mock_callable])
    res = plugin_executor(*args, call=call)
    assert res == 10
    assert mock_callable.call_count == 1

    res = plugin_executor(*args, call=call)

    assert res == 10
    assert mock_callable.call_count == 2


@pytest.fixture
def pickle_path(tmp_path):
    with mock.patch(
        "dagrunner.execute_graph.CONFIG", new=GlobalConfiguration()
    ) as patch_config:
        patch_config._config["dagrunner_runtime"]["cache_dir"] = str(tmp_path)
        patch_config._config["dagrunner_runtime"]["cache_enabled"] = True
    return tmp_path


@pytest.mark.parametrize(
    "side_effect, res, final_call_count",
    [
        [lambda x: x + 5, 10, 1],  # check simple function caching
        [lambda x: None, None, 1],  # check None return caching
    ],
)
def test_cached_execution_enabled(pickle_path, side_effect, res, final_call_count):
    """Test that execution is utilising cache."""
    args = (5,)

    mock_callable = mock.Mock(side_effect=side_effect)
    call = tuple([mock_callable])
    with pytest.warns(
        DeprecationWarning, match="This class is experimental and untested"
    ):
        res = plugin_executor(*args, call=call)
    assert res == res
    assert mock_callable.call_count == 1

    with pytest.warns(
        DeprecationWarning, match="This class is experimental and untested"
    ):
        res = plugin_executor(*args, call=call)

    assert res == res
    assert mock_callable.call_count == final_call_count
