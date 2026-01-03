#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import partial
from kaikout.log import Logger
from kaikout.xmpp.forms import XmppForms
import sys

logger = Logger(__name__)

class XmppAdHoc:


    def add_command(self, node, name, handler):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        self['xep_0050'].add_command(node=node, name=name, handler=handler)
        logger.debug(f'{function_name},,Finish')


    def commands(self):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')

        commands = [
            ['manual',
             '📕 Manual',
              XmppForms.form_manual],
            ['config',
             '🎛️ Configuration',
              XmppForms.form_config],
            ['report',
             '📝 Report',
              XmppForms.form_report],
            ['admin',
             '🗝 Administration',
              XmppForms.form_admin]
        ]

        for node, name, handler in commands:
            XmppAdHoc.add_command(
                self,
                node,
                name,
                partial(handler, self))

        XmppAdHoc.add_command(
            self,
            'about',
            '📜️ About',
            XmppForms.note_about)

#        XmppAdHoc.add_command(
#            self,
#            'about',
#            '📜️ About',
#            lambda session, iq: XmppForms.note_about(self, session, iq))

        logger.debug(f'{function_name},,Finish')
