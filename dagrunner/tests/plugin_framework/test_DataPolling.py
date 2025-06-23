# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from unittest import mock

from dagrunner.plugin_framework import DataPolling


@mock.patch("dagrunner.plugin_framework.data_polling")
def test_data_polling_call(dp_patch):
    dp = DataPolling(
        timeout=mock.sentinel.timeout,
        polling=mock.sentinel.polling,
        verbose=mock.sentinel.verbose,
        file_count=mock.sentinel.file_count,
    )
    dp(
        mock.sentinel.fpath1,
        mock.sentinel.fpath2,
        mock.sentinel.fpath3,
    )
    dp_patch.assert_called_once_with(
        mock.sentinel.fpath1,
        mock.sentinel.fpath2,
        mock.sentinel.fpath3,
        timeout=mock.sentinel.timeout,
        polling=mock.sentinel.polling,
        file_count=mock.sentinel.file_count,
        fail_fast=True,
        verbose=mock.sentinel.verbose,
    )
