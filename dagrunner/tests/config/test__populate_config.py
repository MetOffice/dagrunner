# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import unittest.mock as mock

from dagrunner.config import GlobalConfiguration, _populate_config


def test_file_parse_order():
    mock_config = mock.Mock(GlobalConfiguration)

    with mock.patch(
        "dagrunner.config._DEFAULT_CONFIG_PATHS",
        new=[mock.sentinel.path1, mock.sentinel.path2],
    ):
        _populate_config(mock_config)
    assert mock_config.parse_configuration.call_args_list == [
        mock.call(mock.sentinel.path1),
        mock.call(mock.sentinel.path2),
    ]
