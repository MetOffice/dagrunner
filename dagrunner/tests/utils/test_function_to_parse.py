# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import os
import sys
from io import StringIO

from dagrunner.utils import function_to_argparse

CALLING_MOD = os.path.basename(sys.argv[0])


def assert_help_str(help_str, tar):
    # Remove line wraps for easier comparison
    formatted_help_str = []
    help_strs = help_str.split("\n")
    for line in help_strs:
        if line.startswith("   "):
            # more than 2 space indent
            formatted_help_str[-1] += f" {line.lstrip()}"
        else:
            formatted_help_str.append(line)
    help_str = "\n".join(formatted_help_str)

    if "optional arguments:" in help_str:
        # older versions of argparse use "optional arguments: instead of options:"
        tar = tar.replace("options:", "optional arguments:")
    assert help_str == tar


def get_parser_help_string(parser):
    buffer = StringIO()
    parser.print_help(file=buffer)
    return buffer.getvalue()


def basic_args_kwargs_optional(arg1: int, arg2: str = None, arg3: bool = False):
    """
    Summary line.

    Extended description of function.

    Args:
    - `arg1`: Description of arg1
      further description.
    - `arg2`: Description of arg2.
    - `arg3`: Description of arg3.
      Optional.

    Returns:
    - bool: Description of return value

    """
    return True


def test_basic_args_kwargs_optional():
    """Check function with positional and keyword arguments, one explicitly optional."""
    parser = function_to_argparse(basic_args_kwargs_optional)
    help_str = get_parser_help_string(parser)
    tar = f"""usage: {CALLING_MOD} [-h] --arg2 ARG2 [--arg3] arg1

Summary line.

Extended description of function.

positional arguments:
  arg1         Description of arg1 further description.

options:
  -h, --help   show this help message and exit
  --arg2 ARG2  Description of arg2.
  --arg3       Description of arg3. Optional.
"""
    assert_help_str(help_str, tar)

    args = parser.parse_args(["3", "--arg2", "arg2", "--arg3"])
    assert args.arg1 == 3
    assert args.arg2 == "arg2"
    assert args.arg3 is True


def kwargs_param_expand(**kwargs):
    """
    Summary line.

    Extended description of function.

    Args:
    - `**kwargs`:
        Optional global keyword arguments to apply to all applicable plugins.

    Returns:
    - bool: Description of return value

    """
    return True


def test_kwargs_param_expand():
    """Check function with **kwargs supported."""
    parser = function_to_argparse(kwargs_param_expand)
    help_str = get_parser_help_string(parser)
    tar = f"""usage: {CALLING_MOD} [-h] [--kwargs key value]

Summary line.

Extended description of function.

options:
  -h, --help          show this help message and exit
  --kwargs key value  Optional global keyword arguments to apply to all applicable plugins. Key-value pair argument.
"""  # noqa: E501
    assert_help_str(help_str, tar)

    args = parser.parse_args(["--kwargs", "key1", "val1", "--kwargs", "key2", "val2"])
    assert "kwargs" in args
    assert args.kwargs == {"key1": "val1", "key2": "val2"}


def dict_param(dkwarg1: dict, dkwarg2: dict = None):
    # def dict_param(dkwarg: dict=None):
    """
    Summary line.

    Extended description of function.

    Args:
    - `dkwarg1`: Description of kwarg1.  Optional.
    - `dkwarg2`: Description of kwarg2.

    Returns:
    - bool: Description of return value

    """
    return True


def test_dict_param():
    """Test function with dict arg and kwarg"""
    parser = function_to_argparse(dict_param)
    help_str = get_parser_help_string(parser)
    tar = f"""usage: {CALLING_MOD} [-h] [--dkwarg1 key value] --dkwarg2 key value

Summary line.

Extended description of function.

options:
  -h, --help           show this help message and exit
  --dkwarg1 key value  Description of kwarg1. Optional. Key-value pair argument.
  --dkwarg2 key value  Description of kwarg2. Key-value pair argument.
"""
    assert_help_str(help_str, tar)
    args = parser.parse_args(
        [
            "--dkwarg1",
            "dkwarg1_key1",
            "dkwarg1_val1",
            "--dkwarg1",
            "dkwarg1_key2",
            "dkwarg1_val2",
            "--dkwarg2",
            "dkwarg2_key1",
            "dkwarg2_val1",
            "--dkwarg2",
            "dkwarg2_key2",
            "dkwarg2_val2",
        ]
    )
    assert args.dkwarg1 == {
        "dkwarg1_key1": "dkwarg1_val1",
        "dkwarg1_key2": "dkwarg1_val2",
    }
    assert args.dkwarg2 == {
        "dkwarg2_key1": "dkwarg2_val1",
        "dkwarg2_key2": "dkwarg2_val2",
    }
