# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
import warnings


class DummyWarningApplication:
    def __init__(self, *args, **kwargs):
        warnings.warn("Warning raised during initialisation", UserWarning)

    def __call__(self, *args, **kwargs):
        warnings.warn("Warning raised during execution", UserWarning)
