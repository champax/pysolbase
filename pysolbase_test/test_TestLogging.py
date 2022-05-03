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
import glob
import logging
import os
import unittest
from os.path import dirname, abspath

import gevent

from pysolbase.FileUtility import FileUtility
from pysolbase.SolBase import SolBase
from pysolbase.SysLogger import SysLogger

logger = logging.getLogger(__name__)


class TestLogging(unittest.TestCase):
    """
    Test description
    """

    def setUp(self):
        """
        Setup (called before each test)
        """

        SolBase._reset()

        # Check
        self.assertFalse(SolBase._voodoo_initialized)
        self.assertFalse(SolBase._logging_initialized)

        # Initialize without logging
        SolBase.voodoo_init(init_logging=False)
        self.assertTrue(SolBase._voodoo_initialized)
        self.assertFalse(SolBase._logging_initialized)

        # Re-call => logging must kick in
        SolBase.voodoo_init()
        self.assertTrue(SolBase._voodoo_initialized)
        self.assertTrue(SolBase._logging_initialized)
        SolBase.logging_init("INFO", True)

        # Init
        self.lastMessage = None
        self.onLogCallCount = 0

    def tearDown(self):
        """
        Setup (called after each test)
        """
        pass

    @classmethod
    def print_logger_context(cls):
        """
        Test
        """

        print("*** LOGGERS")
        ar = list()
        ar.append("root")
        ar.extend(list(logging.root.manager.loggerDict))
        for name in ar:
            cur_logger = logging.getLogger(name)
            s = "log=%s, pg=%s, h=%s" % (cur_logger.name, cur_logger.propagate, len(cur_logger.handlers))
            c = cur_logger.parent
            while c is not None:
                s += " => %s(%s, %s)" % (c.name, c.propagate, len(c.handlers))
                c = c.parent
            print(s)

    def _on_log(self, message):
        """
        Log callback
        :param message: Log
        :type message: bytes
        """

        # We receive binary, go to str
        self.lastMessage = SolBase.binary_to_unicode(message)
        print("RECV=%s" % self.lastMessage)
        self.onLogCallCount += 1

    def test_logging_init(self):
        """
        Test
        """

        SolBase.logging_init("INFO", True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")

        SolBase.logging_init("DEBUG", False)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")

        SolBase.logging_init("DEBUG", True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "DEBUG")

        SolBase.logging_init("INFO", True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")

    def test_syslog(self):
        """
        Test
        """

        self.print_logger_context()

        # Syslog is enabled by default
        SolBase.logging_init("INFO", True, log_to_console=False, log_callback=self._on_log)
        SolBase.set_compo_name("COMPO_XXX")

        self.print_logger_context()

        # Emit a log
        self.onLogCallCount = 0
        logger.info("TEST LOG 888")

        self.assertEqual(self.onLogCallCount, 1)
        self.assertIsNotNone(self.lastMessage)
        self.assertGreaterEqual(self.lastMessage.find("TEST LOG 888"), 0)
        self.assertGreaterEqual(self.lastMessage.find("COMPO_XXX:"), 0)
        self.assertGreaterEqual(self.lastMessage.find("| COMPO_XXX |"), 0)
        self.assertGreaterEqual(self.lastMessage.find(SolBase.get_machine_name() + " |"), 0)
        logger.info("Received ==> %s", repr(self.lastMessage))

        # Emit a log (str)
        self.onLogCallCount = 0
        logger.info(repr(u"BUF\u001B\u0BD9\U0001A10D\u1501FUB"))

        self.assertEqual(self.onLogCallCount, 1)
        self.assertIsNotNone(self.lastMessage)
        self.assertGreaterEqual(self.lastMessage.find("BUF"), 0)
        self.assertGreaterEqual(self.lastMessage.find("FUB"), 0)
        self.assertGreaterEqual(self.lastMessage.find("COMPO_XXX:"), 0)
        self.assertGreaterEqual(self.lastMessage.find("| COMPO_XXX |"), 0)
        self.assertGreaterEqual(self.lastMessage.find(SolBase.get_machine_name() + " |"), 0)
        logger.info("Received ==> %s", repr(self.lastMessage))

    def test_log_to_file(self):
        """
        Test
        """

        log_file = "/tmp/pythonsol_unittest.log"

        # Clean
        if FileUtility.is_file_exist(log_file):
            os.remove(log_file)

        # Init
        SolBase.logging_init(log_level="INFO",
                             log_to_file=log_file,
                             log_to_console=True,
                             log_to_syslog=False,
                             log_callback=self._on_log,
                             force_reset=True)
        SolBase.set_compo_name("COMPO_XXX")

        # Emit a log
        logger.info("TEST LOG 888")

        # Emit a log (str)
        logger.info(u"BUF \u001B\u0BD9\U0001A10D\u1501\xc3 FUB")

        # Check the file
        buf = FileUtility.file_to_textbuffer(log_file, "utf-8")

        self.assertIsNotNone(buf)
        self.assertGreaterEqual(buf.find("TEST LOG 888"), 0)

        self.assertGreaterEqual(buf.find("BUF "), 0)
        self.assertGreaterEqual(buf.find(" FUB"), 0)
        self.assertGreaterEqual(buf.find(u"BUF \u001B\u0BD9\U0001A10D\u1501\xc3 FUB"), 0)

        # Simulate a log rotate : kick the file and touch it
        os.remove(log_file)
        FileUtility.append_text_to_file(log_file, "TOTO\n", "utf-8", overwrite=False)

        # Re-emit
        logger.info("TEST LOG 999")

        buf = FileUtility.file_to_textbuffer(log_file, "utf-8")

        self.assertIsNotNone(buf)
        self.assertGreaterEqual(buf.find("TOTO"), 0)
        self.assertGreaterEqual(buf.find("TEST LOG 999"), 0)

    def test_log_to_file_with_filter_greenlet(self):
        """
        Test
        """

        log_file = "/tmp/pythonsol_unittest.log"

        # Clean
        if FileUtility.is_file_exist(log_file):
            os.remove(log_file)

        # Init
        SolBase.logging_init(log_level="INFO",
                             log_to_file=log_file,
                             log_to_console=True,
                             log_to_syslog=False,
                             log_callback=self._on_log,
                             force_reset=True)
        SolBase.set_compo_name("COMPO_XXX")

        # Go
        g1 = gevent.spawn(self._run_filter, "ip001")
        g2 = gevent.spawn(self._run_filter, "ip002")
        gevent.joinall([g1, g2])

        # Re-read and check
        buf = FileUtility.file_to_textbuffer(log_file, "utf-8")

        self.assertGreaterEqual(buf.find("TEST LOG ip_addr=ip001"), 0)
        self.assertGreaterEqual(buf.find("TEST LOG ip_addr=ip002"), 0)

        # Via regex
        for r, b in [
            ["TEST LOG ip_addr=ip001 | k_ip:ip001 z_value:ip001", True],
            ["TEST LOG ip_addr=ip002 | k_ip:ip002 z_value:ip002", True],
            ["TEST LOG ip_addr=ip001 | k_ip:ip002", False],
            ["TEST LOG ip_addr=ip002 | k_ip:ip001", False],
        ]:
            idx = buf.find(r)
            if b:
                self.assertLess(0, idx, r)
            else:
                self.assertGreaterEqual(0, idx, r)

    # noinspection PyMethodMayBeStatic
    def _run_filter(self, ip_addr):

        lo = logging.getLogger("new_logger")
        SolBase.context_set("k_ip", ip_addr)
        SolBase.context_set("z_value", ip_addr)
        SolBase.context_set("zz_uc", u"B\u001BB")

        # Emit a log
        ms = SolBase.mscurrent()
        while SolBase.msdiff(ms) < 2000.0:
            logger.info("TEST LOG ip_addr=%s", ip_addr)
            lo.info("TEST LOG ip_addr=%s", ip_addr)
            SolBase.sleep(0)

    def test_log_to_file_time_file(self):
        """
        Test
        """

        log_file = "/tmp/pythonsol_unittest.log"

        # Clean
        if FileUtility.is_file_exist(log_file):
            os.remove(log_file)

        # Init
        SolBase.logging_init(log_level="INFO",
                             log_to_file=log_file,
                             log_to_console=True,
                             log_to_syslog=False,
                             log_callback=self._on_log,
                             force_reset=True,
                             log_to_file_mode="time_file")
        SolBase.set_compo_name("COMPO_XXX")

        # Emit a log
        logger.info("TEST LOG 888")

        # Emit a log (str)
        logger.info(u"BUF \u001B\u0BD9\U0001A10D\u1501\xc3 FUB")

        # Check the file
        buf = FileUtility.file_to_textbuffer(log_file, "utf-8")

        self.assertIsNotNone(buf)
        self.assertGreaterEqual(buf.find("TEST LOG 888"), 0)

        self.assertGreaterEqual(buf.find("BUF "), 0)
        self.assertGreaterEqual(buf.find(" FUB"), 0)
        self.assertGreaterEqual(buf.find(u"BUF \u001B\u0BD9\U0001A10D\u1501\xc3 FUB"), 0)

    def test_log_to_file_time_file_seconds(self):
        """
        Test
        """

        log_file = "/tmp/pythonsol_unittest.log"

        # Clean
        if FileUtility.is_file_exist(log_file):
            os.remove(log_file)
        for f in glob.glob("/tmp/pythonsol_unittest.log.*"):
            os.remove(f)

        # Init
        SolBase.logging_init(log_level="INFO",
                             log_to_file=log_file,
                             log_to_console=True,
                             log_to_syslog=False,
                             log_callback=self._on_log,
                             force_reset=True,
                             log_to_file_mode="time_file_seconds")
        SolBase.set_compo_name("COMPO_XXX")

        # Emit a log
        logger.info("TEST LOG 888")

        # Emit a log (str)
        logger.info(u"BUF \u001B\u0BD9\U0001A10D\u1501\xc3 FUB")

        # Check the file
        buf = FileUtility.file_to_textbuffer(log_file, "utf-8")

        self.assertIsNotNone(buf)
        self.assertGreaterEqual(buf.find("TEST LOG 888"), 0)

        self.assertGreaterEqual(buf.find("BUF "), 0)
        self.assertGreaterEqual(buf.find(" FUB"), 0)
        self.assertGreaterEqual(buf.find(u"BUF \u001B\u0BD9\U0001A10D\u1501\xc3 FUB"), 0)

        # Wait 5 sec
        for i in range(0, 10):
            SolBase.sleep(1100)
            logger.info("Log i=%s", i)

        # Emit a log
        logger.info("TEST LOG 999")

        # We should have "pythonsol_unittest.log.*" but no more than 7
        f_count = 0
        for f in glob.glob("/tmp/pythonsol_unittest.log.*"):
            logger.info("Found %s", f)
            f_count += 1
        self.assertGreater(f_count, 0)
        self.assertLessEqual(f_count, 7)

        # Reset
        SolBase.logging_init("INFO", True)

    def test_initfromfile_yaml(self):
        """
        Test
        """

        # Conf
        cf = dirname(abspath(__file__)) + os.sep + "logging.yaml"

        # Default
        SolBase.logging_init("INFO", True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")
        self.assertEqual(logging.getLevelName(logging.getLogger("zzz").getEffectiveLevel()), "INFO")

        # Load from file
        SolBase.logging_initfromfile(cf, False)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")
        self.assertEqual(logging.getLevelName(logging.getLogger("zzz").getEffectiveLevel()), "INFO")

        SolBase.logging_initfromfile(cf, True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "DEBUG")
        self.assertEqual(logging.getLevelName(logging.getLogger("zzz").getEffectiveLevel()), "WARNING")

        # Default
        SolBase.logging_init("INFO", True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")
        self.assertEqual(logging.getLevelName(logging.getLogger("zzz").getEffectiveLevel()), "INFO")

    def test_initfromfile_yaml_with_filter(self):
        """
        Test
        """

        # Conf
        cf = dirname(abspath(__file__)) + os.sep + "logging.yaml"

        # Default
        SolBase.logging_init("INFO", True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")
        self.assertEqual(logging.getLevelName(logging.getLogger("zzz").getEffectiveLevel()), "INFO")

        # Load from file
        SolBase.logging_initfromfile(cf, False)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")
        self.assertEqual(logging.getLevelName(logging.getLogger("zzz").getEffectiveLevel()), "INFO")

        SolBase.logging_initfromfile(cf, True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "DEBUG")
        self.assertEqual(logging.getLevelName(logging.getLogger("zzz").getEffectiveLevel()), "WARNING")

        # Register callback (hack it)
        for name in logging.root.manager.loggerDict:
            cur_logger = logging.getLogger(name)
            for h in cur_logger.handlers:
                self.assertIsInstance(h, SysLogger)
                h._log_callback = self._on_log
        for h in logging.root.handlers:
            self.assertIsInstance(h, SysLogger)
            h._log_callback = self._on_log
        SolBase.set_compo_name("COMPO_XXX")

        SolBase.context_set("k_ip", "ZZ01")
        SolBase.context_set("z_value", "ZZ02")
        logger.info("ZLOG")
        self.assertIsNotNone(self.lastMessage)
        self.assertIn("ZLOG", self.lastMessage)
        self.assertIn("k_ip:ZZ01 ", self.lastMessage)
        self.assertIn("z_value:ZZ02 ", self.lastMessage)

        # Default
        SolBase.logging_init("INFO", True)
        self.assertEqual(logging.getLevelName(logging.getLogger().getEffectiveLevel()), "INFO")
        self.assertEqual(logging.getLevelName(logging.getLogger("zzz").getEffectiveLevel()), "INFO")
