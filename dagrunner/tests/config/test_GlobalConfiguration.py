# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import copy
import unittest.mock as mock

import pytest

from dagrunner.config import GlobalConfiguration


@pytest.fixture
def mock_config():
    config = copy.copy(GlobalConfiguration())
    config.__init__()
    return config


@pytest.mark.parametrize(
    "config, target, exception_class, exception_message",
    [
        (
            "",
            {"dagrunner_logging": {}},
            None,
            None,
        ),  # empty config
        (
            "[dagrunner_logging]\nhost=0",
            {"dagrunner_logging": {"host": 0}},
            None,
            None,
        ),  # basic
        (
            "[dagrunner_logging]\nbla=5.0",
            {},
            KeyError,
            'item "bla" are not valid to dagrunner',
        ),  # unrecognised key
        (
            "[dagrunner_bla]\nhost=0",
            {},
            KeyError,
            'dagrunner_bla" and item "host" are not valid to dagrunner',
        ),  # unrecognised group
        (
            "somestuff\n[dagrunner_logging]\nhost=1",
            {"dagrunner_logging": {"host": 1}},
            None,
            None,
        ),  # dirty header
        (
            "[dummy_group]\n[dagrunner_logging]\nhost=1",
            {"dagrunner_logging": {"host": 1}},
            None,
            None,
        ),  # non-dagrunner group ignored
        (
            "#comment0\n[dagrunner_logging] #comment1\nhost=1 #comment2",
            {"dagrunner_logging": {"host": 1}},
            None,
            None,
        ),  # comments
        (
            "[dagrunner_logging]\nhost=$DAGVAR",
            {"dagrunner_logging": {"host": 0}},
            None,
            None,
        ),  # environment variable
    ],
)
def test_parse_configuration(
    mock_config, config, target, exception_class, exception_message
):
    empty_config = mock_config._config.copy()
    patch = mock.patch("dagrunner.config.open", mock.mock_open(read_data=config))
    patch2 = mock.patch(
        "os.path.expandvars", side_effect=lambda x: "0" if x == "$DAGVAR" else x
    )
    with patch, patch2:
        if exception_class:
            with pytest.raises(exception_class, match=exception_message):
                mock_config.parse_configuration(mock.sentinel.fnme)
        else:
            mock_config.parse_configuration(mock.sentinel.fnme)
            assert mock_config._config == empty_config | target


def test_parse_configuration_override(mock_config):
    """
    Check the configuration is correctly overridden.
    """
    config1 = "[dagrunner_logging]\nhost=0"
    patch = mock.patch("dagrunner.config.open", mock.mock_open(read_data=config1))
    with patch:
        mock_config.parse_configuration(mock.sentinel.fnme)
    assert mock_config._config["dagrunner_logging"]["host"] == 0

    config2 = "[dagrunner_logging]\nhost=1"
    patch = mock.patch("dagrunner.config.open", mock.mock_open(read_data=config2))
    with patch:
        mock_config.parse_configuration(mock.sentinel.fnme)
    assert mock_config._config["dagrunner_logging"]["host"] == 1
