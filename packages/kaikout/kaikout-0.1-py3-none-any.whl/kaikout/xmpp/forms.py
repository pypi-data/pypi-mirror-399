#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kaikout.log import Logger
from kaikout.xmpp.dataforms import XmppDataForm
import sys

logger = Logger(__name__)

class XmppForms:


    def form_admin(self, iq, session):
        jid_bare = iq['from'].bare
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        text_note = 'KaikOut Administration Panel.'
        session['notes'] = [['info', text_note]]
        logger.debug(f'{function_name},{jid_bare},Finish')
        return session


    def form_config(self, iq, session):
        jid_bare = iq['from'].bare
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        text_note = 'KaikOut Configuration Panel.'
        session['notes'] = [['info', text_note]]
        logger.debug(f'{function_name},{jid_bare},Finish')
        return session


    def form_manual(self, iq, session):
        jid_bare = iq['from'].bare
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        text_note = 'KaikOut is a moderation service for XMPP.'
        session['notes'] = [['info', text_note]]
        logger.debug(f'{function_name},{jid_bare},Finish')
        return session


    def form_report(self, iq, session):
        jid_bare = iq['from'].bare
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        text_note = 'KaikOut Abuse Report System.'
        session['notes'] = [['info', text_note]]
        logger.debug(f'{function_name},{jid_bare},Finish')
        return session


    def note_about(iq, session):
        jid_bare = iq['from'].bare
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        text_note = 'KaikOut Moderation Service.'
        session['notes'] = [['info', text_note]]
        logger.debug(f'{function_name},{jid_bare},Finish')
        return session


    def note_cancel(payload, session):
        jid_bare = jid_bare
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        text_note = 'Operation has been cancelled.'
        session['notes'] = [['warn', text_note]]
        logger.debug(f'{function_name},{jid_bare},Finish')
        return session


    def note_error(payload, session):
        jid_bare = jid_bare
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        text_note = 'An error has been encountered.'
        session['notes'] = [['error', text_note]]
        logger.debug(f'{function_name},{jid_bare},Finish')
        return session

