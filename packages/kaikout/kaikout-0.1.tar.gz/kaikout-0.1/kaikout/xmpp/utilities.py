#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kaikout.log import Logger
from kaikout.xmpp.muc import XmppMuc
from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = Logger(__name__)


class XmppUtilities:


    async def is_jid_of_moderators(self, room, jid_full):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        # try:
        jid_bare = jid_full.split('/')[0]
        is_jid_of_moderators = False
        moderators = set(await XmppMuc.get_role_list(self, room, 'moderator'))
        for alias in moderators:
            # NOTE You might want to compare jid_bare instead of jid_full
            #if XmppMuc.get_full_jid(self, room, alias) == jid_full:
            jid_full_moderator = XmppMuc.get_full_jid(self, room, alias)
            jid_bare_moderator = jid_full_moderator.split('/')[0]
            if jid_bare == jid_bare_moderator:
                is_jid_of_moderators = True
                break
        # except IqError as e:
        #     logger.error(e)
        logger.debug(f'{function_name},{room},Finish')
        return is_jid_of_moderators


    async def get_chat_type(self, jid_full):
        """
        Check chat (i.e. JID) type.

        If iqresult["disco_info"]["features"] contains XML namespace
        of 'http://jabber.org/protocol/muc', then it is a 'groupchat'.
    
        Unless it has forward slash, which would indicate that it is
        a chat which is conducted through a groupchat.
        
        Otherwise, determine type 'chat'.

        Parameters
        ----------
        jid_full : str
            Jabber ID.

        Returns
        -------
        result : str
            'chat' or 'groupchat' or 'error'.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_full},Start')
        try:
            iqresult = await self["xep_0030"].get_info(jid=jid_full)
            features = iqresult["disco_info"]["features"]
            # identity = iqresult['disco_info']['identities']
            # if 'account' in indentity:
            # if 'conference' in indentity:
            if ('http://jabber.org/protocol/muc' in features) and not ('/' in jid_full):
                result = "groupchat"
            # TODO elif <feature var='jabber:iq:gateway'/>
            # NOTE Is it needed? We do not interact with gateways or services
            else:
                result = "chat"
            logger.info(f'{function_name},{jid_full},Chat Type: {result}')
        except (IqError, IqTimeout) as e:
            logger.error(f'{function_name},{jid_full},Error XmppIQ')
            logger.error(f'{function_name},{jid_full},{str(e)}')
            logger.warning(f'{function_name},{jid_full},Chat type could not be determined.')
            result = 'error'
        # except BaseException as e:
        #     logger.error('BaseException', str(e))
        # finally:
        #     logger.info('Chat type is:', chat_type)
        logger.debug(f'{function_name},{jid_full},Finish')
        return result

    def is_access(self, jid_bare, jid_full, chat_type):
        """Determine access privilege"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        logger.debug(f'{function_name},{jid_bare},JID: {jid_full}; Type: {chat_type}')
        operator = XmppUtilities.is_operator(self, jid_bare)
        if operator:
            if chat_type == 'groupchat':
                if XmppMuc.is_moderator(self, jid_bare, jid_full):
                    access = True
            else:
                access = True
        else:
            access = False
        logger.debug(f'{function_name},{jid_bare},Finish')
        return access

    def is_operator(self, jid_bare):
        """Check if given JID is an operator"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        result = False
        for operator in self.operators:
            if jid_bare == operator['jid']:
                result = True
                # operator_name = operator['name']
                break
        logger.debug(f'{function_name},{jid_bare},Finish')
        return result
