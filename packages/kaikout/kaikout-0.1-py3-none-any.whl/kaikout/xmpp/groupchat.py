#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kaikout.log import Logger, Message
from kaikout.utilities import Toml
from kaikout.xmpp.message import XmppMessage
from kaikout.xmpp.muc import XmppMuc
from kaikout.xmpp.status import XmppStatus
import random
import sys

logger = Logger(__name__)

class XmppGroupchat:

    async def join_to_groupchat(self, room):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        result = await XmppMuc.join_to_muc(self, room)
        if result == 'ban':
            message_body = '{} is banned from {}'.format(self.alias, room)
            jid_bare = message['from'].bare
            XmppMessage.send(self, jid_bare, message_body, 'chat')
            logger.warning(f'{function_name},{room},{message_body}')
        elif result == 'conflict':
            while result == 'conflict':
                number = str(random.randrange(1000, 5000))
                logger.warning(f'{function_name},{room},Conflict. Atempting to join to {room} as {self.alias} #{number}')
                result = await XmppMuc.join_to_muc(self, room, f'{self.alias} #{number}')
        else:
            #self.bookmarks.append({'jid' : room, 'lang' : '', 'pass' : ''})
            if room not in self.bookmarks: self.bookmarks.append(room)
            Toml.save_file(self.filename_bookmarks, self.data_bookmarks)
        logger.debug(f'{function_name},{room},Finish')
        return result

    async def autojoin_to_groupchat(self):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        mucs_joined = []
        for room in self.bookmarks:
            alias = self.alias
            #Message.printer(f'Joining to MUC {room} ...')
            result = await XmppMuc.join_to_muc(self, room)
            if result == 'ban':
                if room in self.bookmarks: self.bookmarks.remove(room)
                Toml.save_file(self.filename_bookmarks, self.data_bookmarks)
                logger.warning(f'{alias} is banned from {room}')
                logger.warning(f'Groupchat {room} has been removed from bookmarks')
            elif result == 'conflict':
                while result == 'conflict':
                    number = str(random.randrange(1000, 5000))
                    logger.warning(f'Conflict. Atempting to join to {room} as {self.alias} #{number}')
                    result = await XmppMuc.join_to_muc(self, room, f'{alias} #{number}')
            else:
                mucs_joined.append(room)
        logger.debug(f'{function_name},,Finish')
        return mucs_joined
