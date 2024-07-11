# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import argparse
import inspect
import time

import dagrunner.utils._doc_styles as doc_styles


class ObjectAsStr(str):
    """Hide object under a string."""

    __slots__ = ("original_object",)

    def __new__(cls, obj, name=None):
        if isinstance(obj, cls):
            # return object as already wrapped
            return obj
        name = cls.obj_to_name(obj, type(obj) if name is None else name)
        self = super().__new__(cls, name)
        self.original_object = obj
        return self

    def __hash__(self):
        # make sure our hash doesn't clash with normal string hash
        return super().__hash__() ^ hash(type(self))

    @staticmethod
    def obj_to_name(obj, cls):
        if isinstance(obj, str):
            return obj
        obj_id = hash(obj) if not isinstance(obj, type) else id(obj)
        return f"<{cls.__module__}.{cls.__name__}@{obj_id}>"


class TimeIt:
    """
    Timer context manager which can also be used as a standalone timer.

    We can query our timer for the elapsed time in seconds even before .

    Example as a context manager:

        >>> with TimeIt() as timer:
        >>>     sleep(0.05)
        >>> print(timer)
        "Elapsed time: 0.05s"

    Example as a standalone timer:

        >>> timer = TimeIt()
        >>> timer.start_timer()
        >>> sleep(0.05)
        >>> print(timer)
        "Elapsed time: 0.05s"

    """

    def __init__(self, verbose=False):
        self._verbose = verbose
        self._total_elapsed = 0
        self._start = None
        self._running = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
        if self._verbose:
            print(str(self))
        return False

    def start(self):
        self._running = True
        self._start = time.perf_counter()

    def stop(self):
        if not self._running:
            raise RuntimeError("Timer is not running.")
        self._total_elapsed = self.elapsed
        self._running = False

    @property
    def elapsed(self):
        """Return elapsed time in seconds."""
        if self._running:
            elapsed = self._total_elapsed + (time.perf_counter() - self._start)
        else:
            elapsed = self._total_elapsed
        return elapsed

    def __str__(self):
        """Print elapsed time in seconds."""
        return f"Elapsed time: {self.elapsed:.2f}s"


def docstring_parse(obj):
    doc = obj.__doc__
    if doc_styles.RSTStyle.is_style(doc):
        parser = doc_styles.RSTStyle(doc)
    elif doc_styles.GoogleStyle.is_style(doc):
        parser = doc_styles.GoogleStyle(doc)
    elif doc_styles.NumpyStyle.is_style(doc):
        parser = doc_styles.NumpyStyle(doc)
    else:
        parser = doc_styles.MDStyle(doc)
    desc = parser.description
    var_mapping = parser.variable_mapping if parser.is_style(doc) else {}
    if var_mapping:
        var_mapping = {k.replace("*", ""): v for k, v in var_mapping.items()}
    return desc, var_mapping


class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        key, value = values
        if not hasattr(namespace, self.dest) or getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, {})
        getattr(namespace, self.dest)[key] = value


# TODO: Support for *args
#       Check signature against docstring (inconsistency)
#       'how it works' docstring
#       more sophisticated support for classes (class.__call__ etc.)
def function_to_argparse(func, parser=None, exclude=None):
    """Generate an argparse from a function signature"""
    if exclude is None:
        exclude = []

    name = func.__name__
    is_method = False
    if isinstance(func, type):
        is_method = True
        func = func.__init__
    func_desc, arg_mapping = docstring_parse(func)
    if parser:
        parser = parser.add_parser(name.replace("_", "-"), help=func_desc)
    else:
        parser = argparse.ArgumentParser(
            description=func_desc, formatter_class=argparse.RawDescriptionHelpFormatter
        )

    sig = inspect.signature(func)
    singature_param = (
        list(sig.parameters.items())[1:] if is_method else sig.parameters.items()
    )
    for name, param in singature_param:
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            print(
                f"'function_to_argparse' parameter expansion '{param}' not "
                "supported yet"
            )
            continue
        if name in exclude:
            continue

        arg_name = name.replace("_", "-")
        arg_type = param.annotation
        arg_default = param.default if param.default is not param.empty else None
        arg_optional = (
            "optional" in arg_mapping[name].lower()
            if name in arg_mapping
            else arg_default is not None
        )
        arg_kwargs = dict(
            type=arg_type,
            default=arg_default,
            help=arg_mapping[name] if name in arg_mapping else None,
        )
        if arg_type is bool:
            arg_kwargs.update(dict(action=f"store_{str(not arg_default).lower()}"))
            arg_kwargs.pop("type")
        elif arg_type in [list, set, tuple]:
            arg_num = "*" if arg_optional else "+"
            arg_kwargs.update(dict(nargs=arg_num))
            arg_kwargs["type"] = str
        elif param.kind == inspect.Parameter.VAR_KEYWORD or arg_type is dict:
            arg_kwargs.pop("type")
            arg_kwargs["nargs"] = 2
            arg_kwargs["action"] = KeyValueAction
            arg_kwargs["metavar"] = ("key", "value")
            arg_kwargs["help"] += "\n Key-value pair argument."
            arg_optional = (
                True if param.kind == inspect.Parameter.VAR_KEYWORD else arg_optional
            )

        if (
            param.default is not param.empty
            or param.kind == inspect.Parameter.VAR_KEYWORD
            or arg_type is dict
        ):
            # is a keywarg
            arg_kwargs["dest"] = name
            arg_kwargs["required"] = not arg_optional
            arg_name = f"--{arg_name}"
        arg_args = [arg_name]
        parser.add_argument(*arg_args, **arg_kwargs)

    return parser
