# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
"""
This module handles the run-time configuration of the dagrunner library.

Certain hooks are present in the library for providing detailed control over
dagrunner run-time.

The configuration of dagrunner follows a first-in first-out approach on parsing
configuration options and is handled by :class:`dagrunner.config.GlobalConfiguration`.
This means that any number of configuration files can be parsed.  On import,
`dagrunner.cfg` is parsed when present in the dagrunner root folder.  Each successive
configuration file parsing will override existing parameter values.
"""

import configparser
import io
import itertools
import os

from .utils import Singleton

_DEFAULT_CONFIG_PATHS = [os.path.join(os.path.dirname(__file__), "dagrunner.cfg")]


class GlobalConfiguration(object, metaclass=Singleton):
    """
    The global configuration class handles any number of configuration files,
    where subsequent configuration entries act to override previous entries
    parsed.

    All group names parsed are prefixed with "dagrunner" and all entries are then
    parsed strictly.  Those groups not with this prefix are silently ignored.

    The following represents a description of the runtime configuration
    options and their default values::

        # Logging

        [dagrunner_logging]
        host
        port

    """

    # Variables defaults should not be defined.  We need to distinguish between
    # specified vs unspecified by the user.
    # Logic around default values belong in the functions which use them.
    _INI_PARAMETERS = {
        "dagrunner_logging": {"host": None, "port": None},
    }

    def __init__(self):
        self._config = {key: {} for key in self._INI_PARAMETERS}
        self._parser = configparser.RawConfigParser()

    def __str__(self):
        return str(self._config)

    def __repr__(self):
        fmt = "{cls}({self._config!r})"
        result = fmt.format(self=self, cls=type(self).__name__)
        return result

    @staticmethod
    def _as_guessed_type(value):
        """Perform appropriate type parsing on configuration files."""

        def convert_type(val):
            val = val.strip()
            try:
                val = eval(val)
            except NameError:
                val = str(val)
            return val

        if "," in value:
            value = value.split(",")
            for ind, val in enumerate(value):
                value[ind] = convert_type(val)
            value = tuple(value)
        else:
            value = convert_type(value)
        return value

    def _get_option(self, section, name):
        """
        Get the value for the specified option under a specified section.

        Correctly removes line ending comments and provides a default return
        value.

        Args:
        - `section`: Section name
        - `name`: Option name

        """
        if (
            section not in self._INI_PARAMETERS
            or name not in self._INI_PARAMETERS[section]
        ):
            msg = (
                'The provided configuration section "{}" and item "{}" are '
                "not valid to dagrunner.  See dagrunner.config for further details."
            )
            raise KeyError(msg.format(section, name))

        if self._parser.has_option(section, name):
            value = self._parser.get(section, name)
            # Expand environmental variables
            value = os.path.expandvars(value)
            value = value.split("#")[0].strip()
            value = self._as_guessed_type(value)
            self._config[section][name] = value

    def parse_configuration(self, filename):
        """
        Parses a new configuration file.

        Entries in 'filename' override existing entries in the configuration,
        while entries not set remain unchanged from the previous state.

        Parameters
        ----------
        filename : str
            Name of the configuration file to read.

        """
        # Ignore file content until the first group (ConfigParser raises a
        # MissingSectionHeaderError otherwise).
        with open(filename, "r") as fh:
            cont = fh.readlines()
        cont = "".join(itertools.dropwhile(lambda x: not x.startswith("["), cont))
        self._parser.read_file(io.StringIO(cont))

        for section in self._parser.sections():
            if section.startswith("dagrunner"):
                # ignore groups which aren't prefixed with "dagrunner".
                for name in self._parser.options(section):
                    self._get_option(section, name)

    def __getitem__(self, key):
        return self._config[key]

    def __setitem__(self, key, value):
        if key not in self._config:
            msg = "Unexpected configuration key: {}".format(key)
            raise ValueError(msg)
        self._config[key] = value


def _populate_config(config):
    for config_file in _DEFAULT_CONFIG_PATHS:
        try:
            config.parse_configuration(config_file)
        except IOError:
            continue


CONFIG = GlobalConfiguration()
_populate_config(CONFIG)
