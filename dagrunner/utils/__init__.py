# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'pp_systems_framework' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import argparse
import inspect
import re
import time

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
    def __init__(self, verbose=False):
        self._verbose = verbose
        self._elapsed = None
        self._start = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self._elapsed = time.perf_counter() - self._start
        if self._verbose:
            print(str(self))

    @property
    def elapsed(self):
        """Return elapsed time in seconds."""
        return self._elapsed

    def __str__(self):
        """Print elapsed time in seconds."""
        return f"Run-time: {self._elapsed}s"


def _extract_arguments_and_descriptions(docstring):
    docstring = docstring.replace('\\*', '*')
    pattern = r'(:param|:keyword) (\*{0,2}\w+):(.+?)(?=\n\s*(?::\s*(?:\w+:)?/|:)|$)'
    matches = re.findall(pattern, docstring, re.DOTALL)
    arguments_and_descriptions = {}

    for match in matches:
        directive, argument_name, description = match
        argument_name = argument_name.strip().replace('*', '')
        description = description.strip()
        arguments_and_descriptions[argument_name] = ' '.join(map(str.strip, description.split('\n')))

    return arguments_and_descriptions

def _docstring_parse(obj):
    from inspect import cleandoc, getdoc
    from sphinx.ext.napoleon.docstring import GoogleDocstring, NumpyDocstring

    if isinstance(obj, str):
        doc = cleandoc(obj)
    else:
        doc = getdoc(obj)
    if not doc:
        return "", {}
    doc = str(GoogleDocstring(str(NumpyDocstring(doc))))
    arg_mapping = _extract_arguments_and_descriptions(doc)
    intro_lines = re.search(r'^(.*?)(?=:param|:keyword|\Z)', doc, re.DOTALL).group(1).strip()
    return intro_lines, arg_mapping,


class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        key, value = values
        if not hasattr(namespace, self.dest) or getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, {})
        getattr(namespace, self.dest)[key] = value


# TODO: Support for *args and **kwargs
#       Check signature against docstring (inconsistency)
#       howitworks docstring
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
    func_desc, arg_mapping = _docstring_parse(func)
    if parser:
        parser = parser.add_parser(name.replace("_", "-"), help=func_desc)
    else:
        parser = argparse.ArgumentParser(
            description=func_desc, formatter_class=argparse.RawDescriptionHelpFormatter
        )

    sig = inspect.signature(func)
    singature_param = list(sig.parameters.items())[1:] if is_method else sig.parameters.items()
    for name, param in singature_param:
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            print(f"'function_to_argparse' parameter expansion '{param}' not supported yet")
            continue
        # if name in exclude:
        #     continue

        arg_name = name.replace("_", "-")
        arg_type = param.annotation
        arg_default = param.default if param.default is not param.empty else None
        arg_optional = "optional" in arg_mapping[name].lower() if name in arg_mapping else arg_default is not None
        arg_kwargs = dict(type=arg_type, default=arg_default, help=arg_mapping[name] if name in arg_mapping else None)
        if arg_type is bool:
            arg_kwargs.update(dict(action=f"store_{str(not arg_default).lower()}"))
            arg_kwargs.pop("type")
        elif arg_type in [list, set, tuple]:
            arg_num = "*" if arg_optional else "+"
            arg_kwargs.update(dict(nargs=arg_num))
            arg_kwargs["type"] = str
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            arg_kwargs.pop("type")
            arg_kwargs["nargs"] = 2
            arg_kwargs["action"] = KeyValueAction
            arg_kwargs["metavar"] = ("key", "value")
            arg_kwargs["help"] += '\n Key-value pair argument.'
            arg_optional = True

        if param.default is not param.empty or param.kind == inspect.Parameter.VAR_KEYWORD:
            # is a keywarg
            arg_kwargs["dest"] = name
            arg_kwargs["required"] = not arg_optional
            arg_name = f"--{arg_name}"
        arg_args = [arg_name]
        parser.add_argument(*arg_args, **arg_kwargs)

    return parser
