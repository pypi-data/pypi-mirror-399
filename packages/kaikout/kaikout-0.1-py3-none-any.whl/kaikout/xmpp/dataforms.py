#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kaikout.log import Logger
import sys

logger = Logger(__name__)

class XmppDataForm:


    def make_form(self, title, instructions):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        form = self['xep_0004'].make_form(
            ftype='form', title=title, instructions=instructions)
        logger.debug(f'{function_name},,Finish')
        return form
