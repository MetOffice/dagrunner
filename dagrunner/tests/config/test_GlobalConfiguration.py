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
            "[dagrunner_visualisation]\nenabled=False",
            {"dagrunner_visualisation": {"enabled": False}},
            None,
            None,
        ),  # basic
        (
            "[dagrunner_visualisation]\nbla=5.0",
            {},
            KeyError,
            'item "bla" are not valid to dagrunner',
        ),  # unrecognised key
        (
            "[dagrunner_bla]\nenabled=False",
            {},
            KeyError,
            'dagrunner_bla" and item "enabled" are not valid to dagrunner',
        ),  # unrecognised group
        (
            "somestuff\n[dagrunner_visualisation]\nenabled=True",
            {"dagrunner_visualisation": {"enabled": True}},
            None,
            None,
        ),  # dirty header
        (
            "[dummy_group]\n[dagrunner_visualisation]\nenabled=True",
            {"dagrunner_visualisation": {"enabled": True}},
            None,
            None,
        ),  # non-dagrunner group ignored
        (
            "#comment0\n[dagrunner_visualisation] #comment1\nenabled=True #comment2",
            {"dagrunner_visualisation": {"enabled": True}},
            None,
            None,
        ),  # comments
        (
            "[dagrunner_visualisation]\nenabled=$DAGVAR",
            {"dagrunner_visualisation": {"enabled": False}},
            None,
            None,
        ),  # environment variable
    ],
)
def test_parse_configuration(
    mock_config, config, target, exception_class, exception_message
):
    patch = mock.patch("dagrunner.config.open", mock.mock_open(read_data=config))
    patch2 = mock.patch(
        "os.path.expandvars", side_effect=lambda x: "False" if x == "$DAGVAR" else x
    )
    with patch, patch2:
        if exception_class:
            with pytest.raises(exception_class, match=exception_message):
                mock_config.parse_configuration(mock.sentinel.fnme)
        else:
            mock_config.parse_configuration(mock.sentinel.fnme)

            ttarget = mock_config._INI_PARAMETERS
            for group in mock_config._INI_PARAMETERS:
                if group in target:
                    ttarget[group].update(target[group])
            assert mock_config._config == ttarget


def test_parse_configuration_override(mock_config):
    """
    Check the configuration is correctly overridden.
    """
    config1 = "[dagrunner_visualisation]\nenabled=False"
    patch = mock.patch("dagrunner.config.open", mock.mock_open(read_data=config1))
    with patch:
        mock_config.parse_configuration(mock.sentinel.fnme)
    assert mock_config._config["dagrunner_visualisation"]["enabled"] is False

    config2 = "[dagrunner_visualisation]\nenabled=True"
    patch = mock.patch("dagrunner.config.open", mock.mock_open(read_data=config2))
    with patch:
        mock_config.parse_configuration(mock.sentinel.fnme)
    assert mock_config._config["dagrunner_visualisation"]["enabled"] is True
