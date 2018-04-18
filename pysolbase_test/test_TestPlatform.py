"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2017 Laurent Labatut / Laurent Champagnac
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
import inspect
import logging
import unittest

from pysolbase import max_int
from pysolbase.PlatformTools import PlatformTools
from pysolbase.SolBase import SolBase
from pysolbase_test.CrashMe import CrashMe

logger = logging.getLogger(__name__)


class TestPlatform(unittest.TestCase):
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

    def test_platform(self):
        """
        Test
        """

        # Just call
        b = PlatformTools.is_cpu_arm()
        self.assertIsInstance(b, bool)

        b = PlatformTools.is_os_64()
        self.assertIsInstance(b, bool)

        s_temp = PlatformTools.get_tmp_dir()
        self.assertGreater(len(s_temp), 0)

        s_dist = PlatformTools.get_distribution_type()
        self.assertIn(s_dist, ["debian", "redhat", "windows"])