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
from pysolbase.SolBase import SolBase
from pysolbase_test.CrashMe import CrashMe

logger = logging.getLogger(__name__)


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
        # Gevent 1.3 : this is buggy (may be related to https://github.com/gevent/gevent/issues/1227)
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
        # Gevent 1.3 : this is buggy (may be related to https://github.com/gevent/gevent/issues/1227)
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
        d = delay_class("dummyName", [0, 10, max_int])

        d.put(0, 5)
        d.put(9, 2)
        d.put(10, 15)
        d.put(19, 1)
        d.put(max_int, 3)

        self.assertEqual(d._sorted_dict[0].get(), 7)
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
            self.assertGreaterEqual(buf.find("e.bytes:[CrashException]"), 0)
            seek_buf = "/pysolbase_test/CrashMe.py@" + str(CrashMe._lineException) + " "
            self.assertGreaterEqual(buf.find(seek_buf), 0, seek_buf)
            seek_buf = "/pysolbase_test/test_TestBase.py@" + str(local_line_exception) + " "
            self.assertGreaterEqual(buf.find(seek_buf), 0, seek_buf)
