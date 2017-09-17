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
import sys
import unittest

from pysol_base.SolBase import SolBase
from pysol_base_test.CrashMe import CrashMe

logger = logging.getLogger("TestBase")


class TestBase(unittest.TestCase):
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

    def test_compo_name(self):
        """
        Test
        """

        self.assertEqual(SolBase.get_compo_name(), "CompoNotSet")
        SolBase.set_compo_name("toto")
        self.assertEqual(SolBase.get_compo_name(), "toto")
        SolBase.set_compo_name("toto2")
        self.assertEqual(SolBase.get_compo_name(), "toto2")

    def test_master_process(self):
        """
        Test
        """

        self.assertEqual(SolBase.get_master_process(), True)
        SolBase.set_master_process(False)
        self.assertEqual(SolBase.get_master_process(), False)
        SolBase.set_master_process(True)
        self.assertEqual(SolBase.get_master_process(), True)

    def test_ms(self):
        """
        Test
        """

        ms = SolBase.mscurrent()
        SolBase.sleep(100)
        self.assertGreaterEqual(SolBase.msdiff(ms), 100)
        self.assertLessEqual(SolBase.msdiff(ms), 200)

    def test_machine_name(self):
        """
        Test
        """

        self.assertIsNotNone(SolBase.get_machine_name())

    def test_date(self):
        """
        Test
        """

        dt = SolBase.datecurrent()
        SolBase.sleep(100)
        self.assertGreaterEqual(SolBase.datediff(dt), 100)
        self.assertLessEqual(SolBase.datediff(dt), 200)

    def test_conversion(self):
        """
        Test
        """

        self.assertEqual(SolBase.to_int(10), 10)
        self.assertEqual(SolBase.to_int("10"), 10)
        self.assertEqual(SolBase.to_int(-10), -10)
        self.assertEqual(SolBase.to_int("-10"), -10)
        self.assertIsInstance(SolBase.to_int(10), int)
        self.assertRaises(Exception, SolBase.to_int, "aaa")

        self.assertEqual(SolBase.to_long(10L), 10L)
        self.assertEqual(SolBase.to_long("10"), 10L)
        self.assertEqual(SolBase.to_long(-10L), -10L)
        self.assertEqual(SolBase.to_long("-10"), -10L)
        self.assertEqual(SolBase.to_long("10"), 10L)
        self.assertIsInstance(SolBase.to_long(10), long)
        self.assertRaises(Exception, SolBase.to_long, "aaa")

        self.assertEqual(SolBase.to_bool(True), True)
        self.assertEqual(SolBase.to_bool(False), False)
        self.assertEqual(SolBase.to_bool("1"), True)
        self.assertEqual(SolBase.to_bool("True"), True)
        self.assertEqual(SolBase.to_bool("0"), False)
        self.assertEqual(SolBase.to_bool("False"), False)
        self.assertIsInstance(SolBase.to_bool(True), bool)
        self.assertIsInstance(SolBase.to_bool(False), bool)
        self.assertRaises(Exception, SolBase.to_bool, "dummy")

    def _go_delay(self, delay_class):
        """
        Test
        :param delay_class: DelayToCount
        :type delay_class: DelayToCount,DelayToCountSafe
        """

        # Misc
        logger.info("Class=%s", delay_class)
        d = delay_class("dummyName", [0, 10, sys.maxint])

        d.put(0, 05)
        d.put(9, 02)
        d.put(10, 15)
        d.put(19, 01)
        d.put(sys.maxint, 3)

        self.assertEqual(d._sorted_dict[0].get(), 07)
        self.assertEqual(d._sorted_dict[10].get(), 19)

        d.log()

    def test_encoder(self):
        """
        Test
        """

        buf = u"BUF\u001B\u0BD9\U0001A10D\u1501FUB"
        bin_buf = SolBase.unicode_to_binary(buf, "utf-8")
        self.assertEqual(buf, SolBase.binary_to_unicode(bin_buf, "utf-8"))

    def test_extostr(self):
        """
        Test
        """

        # Generate a crash
        local_line_exception = inspect.currentframe().f_lineno + 2
        try:
            CrashMe.crash()
        except Exception as e:
            # Convert
            buf = SolBase.extostr(e)

            # Log
            logger.info("e=%s", buf)

            self.assertGreaterEqual(buf.find("e.cls:[Exception]"), 0)
            self.assertGreaterEqual(buf.find("e.str:[CrashException]"), 0)
            seek_buf = "/pysol_base_test/CrashMe.py@" + str(CrashMe._lineException) + " "
            self.assertGreaterEqual(buf.find(seek_buf), 0, seek_buf)
            seek_buf = "/pysol_base_test/TestBase.py@" + str(local_line_exception) + " "
            self.assertGreaterEqual(buf.find(seek_buf), 0, seek_buf)
