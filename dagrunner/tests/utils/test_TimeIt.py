# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from time import sleep

from dagrunner.utils import TimeIt


def timer_equal(timer, expected):
    tolerance = 0.1
    return abs(timer.elapsed - expected) <= tolerance


def test_context_manager():
    with TimeIt() as timer:
        sleep(0.05)
        assert timer_equal(timer, 0.05)
        sleep(0.05)
    assert timer_equal(timer, 0.1)


def test_standalone():
    """Test the standalone timer where we can start-stop it."""
    timer = TimeIt()
    timer.start()
    sleep(0.05)
    assert timer_equal(timer, 0.05)

    sleep(0.05)
    timer.stop()
    sleep(0.05)

    assert timer_equal(timer, 0.1)
    timer.start()
    sleep(0.05)
    assert timer_equal(timer, 0.15)


def test___str__():
    timer = TimeIt()
    timer._total_elapsed = 0.0598723
    assert str(timer) == "Elapsed time: 0.06s"
