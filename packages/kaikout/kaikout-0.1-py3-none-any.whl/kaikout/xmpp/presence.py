#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kaikout.log import Logger
import sys

logger = Logger(__name__)

class XmppPresence:


    def send(self, jid, status_message, presence_type=None, status_type=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid},Start')
        logger.debug(f'{function_name},{jid},{status_message}')
        jid_from = str(self.boundjid) if self.is_component else None
        self.send_presence(pto=jid,
                           pfrom=jid_from,
                           pshow=status_type,
                           pstatus=status_message,
                           ptype=presence_type)
        logger.debug(f'{function_name},{jid},Finish')


    def subscription(self, jid, presence_type):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid},Start')
        logger.debug(f'{function_name},{jid},{presence_type}')
        self.send_presence_subscription(pto=jid,
                                        pfrom=self.boundjid.bare,
                                        ptype=presence_type,
                                        pnick=self.alias)
        logger.debug(f'{function_name},{jid},Finish')
