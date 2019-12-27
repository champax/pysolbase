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

# noinspection PyMethodMayBeStatic

# noinspection PyMethodMayBeStatic
from gevent.local import local


class ContextFilter(object):
    """
    Context filter
    DOC : https://docs.python.org/3/howto/logging-cookbook.html#adding-contextual-information-to-your-logging-output
    """

    # ===============================
    # CAUTION : We must target local here (otherwise its local function variables)
    # ===============================
    LOC = local()

    # ===============================
    # SET / STATIC (easier for external calls)
    # ===============================

    @classmethod
    def remote_addr_set(cls, remote_addr):
        """
        Set remote addr
        :param remote_addr: str,None
        :type remote_addr: str,None
        """

        # Store it
        cls.LOC.k_ip = remote_addr

    # ===============================
    # GET / NON STATIC (easier for D_FILTER)
    # ===============================

    def remote_addr_get(self):
        """
        Get remote addr from thread locals
        :return None,basestring
        :rtype None,basestring
        """

        try:
            return self.LOC.k_ip
        except AttributeError:
            return None

    # ===============================
    # Dictionary KEY to method
    # WILL be appended to logger formatters
    # ===============================
    D_FILTER = {
        "k_ip": remote_addr_get,
    }

    # ===============================
    # FILTER
    # ===============================

    def filter(self, record):
        """
        Record filter.
        :param record: logging.LogRecord
        :type record: logging.LogRecord
        :return: bool
        :rtype bool
        """

        # Push
        for k, m in self.D_FILTER.items():
            # Get value from thread local
            v = m(self)
            # Push to record
            setattr(record, k, v)

        return True
