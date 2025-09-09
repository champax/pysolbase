"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2025 Laurent Labatut / Laurent Champagnac
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

from pysolbase.FlagTools import FlagTools
from pysolbase.SolBase import SolBase

logger = logging.getLogger(__name__)
SolBase.voodoo_init()


class TestFlagTools(unittest.TestCase):
    """
    Test description
    """

    def setUp(self):
        """
        Test
        """
        pass

    def tearDown(self):
        """
        Test
        """
        pass

    def test_flag_tools(self):
        """
        Test
        """

        for i in range(0, 32):
            logger.info("i=%s", i)
            flag = 1 << i

            # Init
            v = 0

            # Check
            r = FlagTools.is_set(v, flag)
            logger.info("v=%s, flag=%s, r=%s", v, flag, r)
            self.assertFalse(r)

            # Add it
            v = FlagTools.set(v, flag)

            # Check
            r = FlagTools.is_set(v, flag)
            logger.info("v=%s, flag=%s, r=%s", v, flag, r)
            self.assertTrue(r)

            # Remove it
            v = FlagTools.clear(v, flag)
            r = FlagTools.is_set(v, flag)
            logger.info("v=%s, flag=%s, r=%s", v, flag, r)
            self.assertFalse(r)
