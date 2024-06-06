from dagrunner.utils import docstring_parse
import pytest


def markdown_style(arg1, arg2=None):
    """
    Summary line.

    Extended description of function.

    Args:
    - `arg1` (int): Description of arg1
      further description.
    - `arg2` (str): Description of arg2, defaults to None

    Returns:
    - bool: Description of return value

    """
    return True


def rst_style(arg1, arg2=None):
    """
    Summary line.

    Extended description of function.

    :param arg1: Description of arg1
        further description.
    :type arg1: int
    :param arg2: Description of arg2, defaults to None
    :type arg2: str, optional

    :return: Description of return value
    :rtype: bool
    """
    return True


def google_style(arg1, arg2=None):
    """
    Summary line.

    Extended description of function.

    Args:
        arg1 (int): Description of arg1
            further description.
        arg2 (str, optional): Description of arg2, defaults to None

    Returns:
        bool: Description of return value

    """
    return True


def numpy_style(arg1, arg2=None):
    """
    Summary line.

    Extended description of function.

    Parameters
    ----------
    arg1 : int
        Description of arg1
        further description.
    arg2 : str, optional
        Description of arg2, defaults to None

    Returns
    -------
    bool
        Description of return value

    """
    return True


def non_style():
    """
    Summary line.

    Extended description of function.
    """
    return True


def non_style_v2():
    """Summary line.

    Extended description of function.
    """
    return True


@pytest.mark.parametrize("func", [numpy_style, google_style, rst_style, markdown_style])
def test_docstring_parse(func):
    intro_lines, arg_mapping = docstring_parse(func)
    assert intro_lines == "Summary line.\n\nExtended description of function."
    assert arg_mapping == {
        "arg1": "Description of arg1 further description.",
        "arg2": "Description of arg2, defaults to None",
    }


@pytest.mark.parametrize("func", [non_style, non_style_v2])
def test_docstring_parse_no_style(func):
    intro_lines, arg_mapping = docstring_parse(func)
    assert intro_lines == "Summary line.\n\nExtended description of function."
    assert arg_mapping == {}
