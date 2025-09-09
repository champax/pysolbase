"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2025 Laurent Labatut / Laurent Champagnac
#
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""
import logging
import unittest

from pysolbase.Assert import Assert
from pysolbase.SolBase import SolBase

logger = logging.getLogger(__name__)


class LocalException(Exception):
    """
    For test
    """

    def __init__(self, message, param1=None):
        """
        Test.

        :param message: text message
        :type message: str
        :param param1: test
        :type param1: object
        """
        self.param1 = param1
        super(LocalException, self).__init__(message)


class TestAssert(unittest.TestCase):
    """
    Test description
    """

    def setUp(self):
        """
        Setup (called before each test)
        """

        # Initialize asap
        SolBase.voodoo_init()
        SolBase.set_compo_name("CompoNotSet")
        self.assertTrue(SolBase._voodoo_initialized)
        self.assertTrue(SolBase._logging_initialized)

    def tearDown(self):
        """
        Setup (called after each test)
        """
        pass

    def test_true(self):
        """
        Test
        """
        self.assertTrue(True)

    # noinspection PyBroadException
    def test_check(self):
        """
        Test
        """

        Assert.check(Exception, 1 == 1, "Must no raise")
        self.assertRaises(Exception, Assert.check, Exception, 1 == 2, "Must raise")

        Assert.check(Exception, ["a"], "Must no raise")
        self.assertRaises(Exception, Assert.check, Exception, [], "Must raise")

        # noinspection PyRedundantParentheses
        Assert.check(Exception, ("a"), "Must no raise")
        self.assertRaises(Exception, Assert.check, Exception, (), "Must raise")

        Assert.check(Exception, {"a": 1}, "Must no raise")
        self.assertRaises(Exception, Assert.check, Exception, {}, "Must raise")

        try:
            Assert.check(LocalException, 1 == 2, "Must raise zzz")
            self.fail("Must raise")
        except LocalException as e:
            self.assertIn("Must raise zzz", str(e))
        except Exception:
            self.fail("Must raise StandardError")

    def test_check_custom_params(self):
        """
        Test.
        """
        try:
            Assert.check(LocalException, False, 'test_987', param1='custom')
            self.assertTrue(False, 'must raise before')
        except LocalException as e:
            self.assertEqual(e.param1, 'custom')
            self.assertIn("test_987", str(e))
