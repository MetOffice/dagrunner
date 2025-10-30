# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from dagrunner.utils import Singleton


class _EventBase:
    def __repr__(self):
        # Ensures easy identification when printing/logging.
        return self.__class__.__name__.upper()

    def __hash__(self):
        # Ensures that can be used as keys in dictionaries or stored as sets.
        return hash(self.__class__.__name__.upper())

    def __reduce__(self):
        # Ensures that can be serialised and deserialised using pickle.
        return (self.__class__, ())


class _SkipEvent(_EventBase, metaclass=Singleton):
    """
    A plugin that returns a 'SKIP_EVENT' will cause `plugin_executor` to skip execution
    of all descendant node execution.
    """

    pass


SKIP_EVENT = _SkipEvent()


class _IgnoreEvent(_EventBase, metaclass=Singleton):
    """
    A plugin that returns an 'IGNORE_EVENT' will be filtered out as arguments by
    `plugin_executor` in descendant node execution.
    """

    pass


IGNORE_EVENT = _IgnoreEvent()
