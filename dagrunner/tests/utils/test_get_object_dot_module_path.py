# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import pytest

from dagrunner.utils import get_object_dot_module_path


class DummyClass:
    pass


def dummy_function():
    return True


@pytest.mark.parametrize(
    "obj, expected",
    [
        ("module.path.object", "module.path.object"),
        (DummyClass, f"{DummyClass.__module__}.{DummyClass.__name__}"),
        (DummyClass(), f"{DummyClass.__module__}.{DummyClass.__name__}"),
        (dummy_function, f"{dummy_function.__module__}.{dummy_function.__name__}"),
    ],
)
def test_get_object_dot_module_path(obj, expected):
    """Return object path for string, type, instance and function inputs."""
    assert get_object_dot_module_path(obj) == expected


def test_get_object_dot_module_path_function_instance():
    """Nested function objects return builtins.function."""

    def test_func():
        return True

    assert get_object_dot_module_path(test_func) == "builtins.function"
