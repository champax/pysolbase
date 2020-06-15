"""
# -*- coding: utf-8 -*-
# ===============================================================================
# Copyright (C) 2017 Vulog SAS
# ===============================================================================
"""


class Assert(object):
    """
    Assert helpers
    """

    @classmethod
    def check(cls, exception_class, condition, message):
        """
        Check a condition and, if false, raise provided exception with provided message.
        :param exception_class: Exception class to raise if condition is False.
        :type exception_class: callable
        :param condition: Condition to evaluate. If false, will raise. If dict|tuple|list is empty, will raise.
        :type condition: bool,list,tuple,dict
        :param message: Exception message
        :type message: basestring
        """

        if condition:
            return

        raise exception_class(message)
