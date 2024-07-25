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
        return (
            f"iarg1={self._iarg1}; ikwarg1={self._ikwarg1}; args={args}; "
            f"kwarg1={kwarg1}; kwargs={kwargs}"
        )


@mock.patch("dagrunner.execute_graph.logger.client_attach_socket_handler")
def test_pass_class_arg_kwargs(mock_client_attach_socket_handler):
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
    assert res == (
        "iarg1=sentinel.iarg1; ikwarg1=sentinel.ikwarg1; "
        "args=(sentinel.arg1, sentinel.arg2); kwarg1=sentinel.kwarg1; "
        "kwargs={}"
    )


@mock.patch("dagrunner.execute_graph.logger.client_attach_socket_handler")
def test_pass_common_args(mock_client_attach_socket_handler):
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
    assert res == (
        "iarg1=sentinel.iarg1; ikwarg1=None; args=(sentinel.arg1, "
        "sentinel.arg2); kwarg1=None; kwargs={}"
    )

    # call with common args
    call = tuple([DummyPlugin, {}, {}])
    res = plugin_executor(*args, call=call, common_kwargs=common_kwargs)
    assert res == (
        "iarg1=sentinel.iarg1; ikwarg1=sentinel.ikwarg1; "
        "args=(sentinel.arg1, sentinel.arg2); kwarg1=sentinel.kwarg1; "
        "kwargs={}"
    )


class DummyPlugin2:
    """Plugin that is reliant on data not explicitly defined in its UI."""

    def __call__(self, *args, **kwargs):
        return f"args={args}; kwargs={kwargs}"


@mock.patch("dagrunner.execute_graph.logger.client_attach_socket_handler")
def test_pass_common_args_via_override(mock_client_attach_socket_handler):
    """
    Passing 'common args' to a plugin that doesn't have such arguments
    defined in its signature.  Instead, filter out those that aren't
    specified in the graph.
    """
    common_kwargs = {
        "kwarg1": mock.sentinel.kwarg1,
        "kwarg2": mock.sentinel.kwarg2,
        "kwarg3": mock.sentinel.kwarg3,
    }
    args = []
    call = tuple(
        [
            DummyPlugin2,
            {
                "kwarg1": mock.sentinel.kwarg1,
                "kwarg2": mock.sentinel.kwarg2,
            },
        ]
    )
    res = plugin_executor(*args, call=call, common_kwargs=common_kwargs)
    assert (
        res == "args=(); kwargs={'kwarg1': sentinel.kwarg1, 'kwarg2': sentinel.kwarg2}"
    )
