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

from logging.handlers import SysLogHandler
import socket

from gevent import GreenletExit

from pysolbase.SolBase import SolBase


# noinspection PyPep8
class SysLogger(SysLogHandler):
    """
    Sys log handler (will format and emit logs toward rsyslog)
    """

    def __init__(self, address="/dev/log", facility=SysLogHandler.LOG_LOCAL1, socktype=socket.SOCK_DGRAM,
                 log_callback=None):
        """
        Init
        :param address: tuple ('ip', port) or string "target"
        :type address:  str, tuple
        :param facility: log facility
        :type facility: int
        :param socktype: Type of socket
        :type socktype: socket.SocketKind
        :param log_callback: Callback for unit test
        """

        # To avoid some warnings
        self.socket = None
        self.address = address

        # Store
        self._log_callback = log_callback
        self.socktype = socktype

        # Base call
        SysLogHandler.__init__(self, address=address, facility=facility, socktype=socktype)

    def _ensure_socket(self):
        """
        Ensure socket is created and connected.
        Backward-compatible across Python 3.7, 3.11, and 3.13+.
        """
        if self.socket is not None:
            return

        if hasattr(self, "createSocket"):
            # Python 3.8+ / 3.10+ / 3.11 / 3.13
            try:
                self.createSocket()
            except OSError:
                pass
        elif self.unixsocket:
            # Python 3.7 unix socket fallback
            try:
                self._connect_unixsocket(self.address)
            except OSError:
                pass
        else:
            # Python 3.7 network socket fallback
            try:
                use_socktype = self.socktype if self.socktype is not None else socket.SOCK_DGRAM
                self.socket = socket.socket(socket.AF_INET, use_socktype)
                if use_socktype == socket.SOCK_STREAM:
                    self.socket.connect(self.address)
            except OSError:
                pass

    def notify_log(self, msg):
        """
        Notify log to callback if set (unittest purpose)
        :param msg: Log message
        :type msg: str,bytes
        """
        # noinspection PyBroadException
        try:
            if self._log_callback:
                self._log_callback(msg)
        except:
            pass

    def emit(self, record):
        """
        Emit a record.
        :param record: The record to log
        :type record: logging.LogRecord
        """

        # Write
        # noinspection PyBroadException
        try:
            # Format
            msg = self.format(record) + '\000'

            # Get component name
            cn = SolBase.get_compo_name()

            # We append the machine+component name at the beginning
            msg = u"{0} | {1} | {2}".format(SolBase.get_machine_name(), cn, msg)
            msg = msg.encode('utf-8')

            # Add priority + facility (int)
            priority = '<%d>' % self.encodePriority(self.facility, self.mapPriority(record.levelname))
            priority = priority.encode('utf-8')

            # Cn
            cn = cn.encode('utf-8')

            # noinspection PyAugmentAssignment
            msg = priority + cn + b": " + msg

            # Notify
            self.notify_log(msg)

            # Send to socket
            if self.socket is None:
                self._ensure_socket()

            if self.unixsocket:
                try:
                    if self.socket is not None:
                        self.socket.send(msg)
                except socket.error:
                    # noinspection PyUnresolvedReferences
                    try:
                        if self.socket is not None:
                            self.socket.close()
                    except Exception:
                        pass
                    self.socket = None
                    self._ensure_socket()
                    if self.socket is not None:
                        self.socket.send(msg)
            elif self.socktype == socket.SOCK_DGRAM:
                if self.socket is not None:
                    self.socket.sendto(msg, self.address)
            else:
                if self.socket is not None:
                    try:
                        self.socket.sendall(msg)
                    except socket.error:
                        try:
                            if self.socket is not None:
                                self.socket.close()
                        except Exception:
                            pass
                        self.socket = None
                        self._ensure_socket()
                        if self.socket is not None:
                            self.socket.sendall(msg)
        except GreenletExit:
            pass
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
