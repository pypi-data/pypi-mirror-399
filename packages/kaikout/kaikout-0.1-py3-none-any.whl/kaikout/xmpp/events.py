#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime
from functools import partial
from kaikout.about import Documentation
from kaikout.database import DatabaseToml, Record
from kaikout.log import Logger
from kaikout.utilities import Config, BlockList, Toml
from kaikout.xmpp.adhoc import XmppAdHoc
from kaikout.xmpp.chat import XmppChat
from kaikout.xmpp.commands import XmppCommands
from kaikout.xmpp.groupchat import XmppGroupchat
from kaikout.xmpp.message import XmppMessage
from kaikout.xmpp.muc import XmppMuc
from kaikout.xmpp.observation import XmppObservation
from kaikout.xmpp.pubsub import XmppPubsub
from kaikout.xmpp.status import XmppStatus
import os
import slixmpp
import sys
import time

logger = Logger(__name__)

class XmppEvents:


    def muc_online(self, presence):
        """
        Process a presence stanza from a chat room. In this case,
        presences from users that have just come online are
        handled by sending a welcome message that includes
        the user's nickname and role in the room.

        Arguments:
            presence -- The received presence stanza. See the
                        documentation for the Presence stanza
                        to see how else it may be used.
        """
        presence_muc_nick = presence['muc']['nick']
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{presence_muc_nick},Start')
        if presence_muc_nick != self.alias:
            presence_muc_role = presence['muc']['role']
            self.send_message(mto=presence['from'].bare,
                              mbody=f'Greetings, {presence_muc_role} {presence_muc_nick}',
                              mtype='groupchat')
        logger.debug(f'{function_name},{presence_muc_nick},Finish')


    async def on_disco_info(self, DiscoInfo):
        jid = DiscoInfo['from']
        jid_bare = jid.bare
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        await self['xep_0115'].update_caps(jid=jid)
        logger.debug(f'{function_name},{jid_bare},Finish')


    # TODO Test
    async def on_groupchat_invite(self, message):
        jid = message['from']
        jid_bare = jid.bare
        #jid_full = jid.full
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        room = message['groupchat_invite']['jid']
        result = await XmppGroupchat.join_to_groupchat(self, room)
        if result != 'ban':
            #self.bookmarks.append({'jid' : room, 'lang' : '', 'pass' : ''})
            if room not in self.bookmarks: self.bookmarks.append(room)
            Toml.save_file(self.filename_bookmarks, self.data_bookmarks)
            XmppStatus.send_status_message(self, room)
            self.add_event_handler(f'muc::{room}::got_online',
                partial(XmppEvents.on_muc_got_online, self))
            self.add_event_handler(f'muc::{room}::presence',
                partial(XmppEvents.on_muc_presence, self))
            self.add_event_handler(f'muc::{room}::self-presence',
                partial(XmppEvents.on_muc_self_presence, self))


    async def on_groupchat_direct_invite(self, message):
        room = message['groupchat_invite']['jid']
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        result = await XmppGroupchat.join_to_groupchat(self, room)
        if result != 'ban':
            #self.bookmarks.append({'jid' : room, 'lang' : '', 'pass' : ''})
            if room not in self.bookmarks: self.bookmarks.append(room)
            Toml.save_file(self.filename_bookmarks, self.data_bookmarks)
            XmppStatus.send_status_message(self, room)
            self.add_event_handler(f'muc::{room}::got_online',
                partial(XmppEvents.on_muc_got_online, self))
            self.add_event_handler(f'muc::{room}::presence',
                partial(XmppEvents.on_muc_presence, self))
            self.add_event_handler(f'muc::{room}::self-presence',
                partial(XmppEvents.on_muc_self_presence, self))
        logger.debug(f'{function_name},{room},Finish')


    async def on_message(self, message):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        await XmppChat.process_message(self, message)
        # if message['type'] == 'groupchat':
        # if 'mucroom' in message.keys():
        if message.get_plugin('muc', check=True):
            room = message['muc']['room']
            alias = message['muc']['nick']
            message_body = message['body']
            identifier = message['id']
            lang = message['lang']
            timestamp_iso = datetime.now().isoformat()
            fields = ['message', timestamp_iso, alias, message_body, lang, identifier]
            filename = datetime.today().strftime('%Y-%m-%d') + '_' + room
            Record.csv(filename, fields)
            db_file = DatabaseToml.instantiate(self, room)
            timestamp = time.time()
            jid_full = XmppMuc.get_full_jid(self, room, alias)
            if jid_full and '/' in jid_full:
                jid_bare = jid_full.split('/')[0]
                XmppCommands.update_last_activity(
                    self, room, jid_bare, db_file, timestamp)
                # DatabaseToml.load_jid_settings(self, room)
                # await XmppChat.process_message(self, message)
                if (XmppMuc.is_moderator(self, room, self.alias) and
                    self.settings[room]['enabled'] and
                    alias != self.alias and
                    jid_bare and
                    jid_bare not in self.settings[room]['jid_whitelist']):
                    identifier = message['id']
                    fields = [alias, message_body, identifier, timestamp]
                    Record.toml(self, room, fields, 'message')
                    # Check for message
                    await XmppObservation.observe_message(
                        self, db_file, alias, message_body, room)
                    # Check for inactivity
                    await XmppObservation.observe_inactivity(
                        self, db_file, room)
        logger.debug(f'{function_name},,Finish')


    async def on_muc_got_online(self, presence):
        room = presence['muc']['room']
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        alias = presence['muc']['nick']
        presence_body = 'User has joined to the groupchat.'
        identifier = presence['id']
        lang = presence['lang']
        timestamp_iso = datetime.now().isoformat()
        fields = ['message', timestamp_iso, alias, presence_body, lang, identifier]
        filename = datetime.today().strftime('%Y-%m-%d') + '_' + room
        Record.csv(filename, fields)
        jid_bare = presence['muc']['jid'].bare
        fields = [jid_bare, alias, timestamp_iso]
        if jid_bare:
            if not Record.jid_exist(room, fields):
                Record.csv_jid(room, fields)
            elif not Record.alias_jid_exist(room, fields):
                Record.csv_jid(room, fields)
            if jid_bare not in self.settings[room]['last_activity']:
                message_body = (f'Welcome, {alias}! We hope that you would '
                                f'have a good time at group chat {room}.')
                # NOTE Check to which resource the message is sent.
                jid_full = XmppMuc.get_full_jid(self, room, alias)
                XmppMessage.send(self, jid_full, message_body, 'chat')
        if (XmppMuc.is_moderator(self, room, self.alias) and
            self.settings[room]['enabled'] and
            jid_bare and
            jid_bare not in self.settings[room]['jid_whitelist']):
            await XmppObservation.observe_jid(self, alias, jid_bare, room)
            # message_body = 'Greetings {} and welcome to groupchat {}'.format(alias, room)
            # XmppMessage.send(self, jid.bare, message_body, 'chat')
            # Send MUC-PM in case there is no indication for reception of 1:1
            # jid_from = presence['from']
            # XmppMessage.send(self, jid_from, message_body, 'chat')
        logger.debug(f'{function_name},{room},Finish')


    async def on_muc_presence(self, presence):
        room = presence['muc']['room']
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        alias = presence['muc']['nick']
        identifier = presence['id']
        jid_bare = presence['muc']['jid'].bare
        lang = presence['lang']
        status_codes = presence['muc']['status_codes']
        actor_alias = presence['muc']['item']['actor']['nick']
        # Leave group chat upon code 301 (ban) or 307 (kick).
        if jid_bare == self.boundjid.bare and (
            301 in status_codes or 307 in status_codes):
            await XmppCommands.muc_leave(self, room)
            presence_body = (
                'KaikOut has left the group chat. Reason: Received '
                f'status code {str(status_codes)} by {actor_alias}')
        elif 301 in status_codes:
            presence_body = f'User has been banned by {actor_alias}'
        elif 307 in status_codes:
            presence_body = f'User has been kicked by {actor_alias}'
        else:
            presence_body = presence['status']
        timestamp_iso = datetime.now().isoformat()
        fields = ['presence', timestamp_iso, alias, presence_body, lang, identifier]
        filename = datetime.today().strftime('%Y-%m-%d') + '_' + room
        # if identifier and presence_body:
        Record.csv(filename, fields)
        db_file = DatabaseToml.instantiate(self, room)
        if (XmppMuc.is_moderator(self, room, self.alias) and
            self.settings[room]['enabled'] and
            alias != self.alias):
            timestamp = time.time()
            fields = [alias, presence_body, identifier, timestamp]
            Record.toml(self, room, fields, 'presence')
            # Count bans and kicks
            await XmppObservation.observe_strikes(self, db_file, presence, room)
            if jid_bare and jid_bare not in self.settings[room]['jid_whitelist']:
                # Check for status message
                await XmppObservation.observe_status_message(
                    self, alias, db_file, jid_bare, presence_body, room)
                # Check for inactivity
                await XmppObservation.observe_inactivity(self, db_file, room)
        logger.debug(f'{function_name},{room},Finish')


    def on_muc_self_presence(self, presence):
        room = presence['muc']['room']
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        actor = presence['muc']['item']['actor']['nick']
        alias = presence['muc']['nick']
        if actor and alias == self.alias:
            XmppStatus.send_status_message(self, room)
        # TODO Check whether group chat is not anonymous
        if XmppMuc.is_moderator(self, room, self.alias):
            timestamp_iso = datetime.now().isoformat()
            db_file = DatabaseToml.instantiate(self, room)
            timestamp = time.time()
            for p_alias in XmppMuc.get_roster(self, room):
                jid_full = XmppMuc.get_full_jid(self, room, p_alias)
                # Upon changing role to moderator, the second
                # time (i.e. loop) would return values.
                if jid_full:
                    jid_bare = jid_full.split('/')[0]
                    fields = [jid_bare, p_alias, timestamp_iso]
                    if not Record.jid_exist(room, fields):
                        Record.csv_jid(room, fields)
                    elif not Record.alias_jid_exist(room, fields):
                        Record.csv_jid(room, fields)
                    # NOTE It seems that there is a difficulty to determine an
                    # alias when the same JID is conected from two different
                    # resources with two different aliases
                    #if p_alias == self.settings[room]['last_alias'][jid_bare]:
                    if jid_bare not in self.settings[room]['last_activity']:
                        XmppCommands.update_last_activity(
                            self, room, jid_bare, db_file, timestamp)
                    XmppCommands.update_last_alias(
                        self, room, jid_bare, db_file, p_alias)
        logger.debug(f'{function_name},{room},Finish')


    def on_reactions(self, message):
        room = message['muc']['room']
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        reactions = message['reactions']['values']
        alias = message['muc']['nick']
        affiliation = XmppMuc.get_affiliation(self, room, alias)
        if affiliation == 'member' and '👎' in reactions:
            message_body = '{} {} has reacted to message {} with {}'.format(
                affiliation, alias, message['id'], message['reactions']['plugin']['value'])
            message.reply(message_body).send()
            logger.info(message_body)
        logger.debug(f'{function_name},{room},Finish')


    def on_room_activity(self, presence):
        print('on_room_activity')
        print(presence)
        print('testing mix core')
        breakpoint()


    async def on_session_start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        XmppAdHoc.commands(self)
        # await self.get_roster()
        rtbl_sources = self.data_rtbl['sources']
        for source in rtbl_sources:
            jabber_id = source['jabber_id']
            node_id = source['node_id']
            subscribe = await XmppPubsub.subscribe(self, jabber_id, node_id)
            if subscribe['pubsub']['subscription']['subscription'] == 'subscribed':
                rtbl_list = await XmppPubsub.get_items(self, jabber_id, node_id)
                rtbl_items = rtbl_list['pubsub']['items']
                muc_bans_sha256 = self.blocklist['entries']['xmppbl.org']['muc_bans_sha256']
                for item in rtbl_items:
                    item_id = item['id']
                    if item_id not in muc_bans_sha256: muc_bans_sha256.append(item_id)
                    # TODO Extract items item_payload.find(namespace + 'title')
                    # NOTE (Pdb)
                    # for i in item['payload'].iter(): i.attrib
                    # {'reason': 'urn:xmpp:reporting:abuse'}
                self.blocklist['entries']['xmppbl.org']['muc_bans_sha256'] = muc_bans_sha256
                Toml.save_file(self.filename_blocklist, self.blocklist)
                del self.filename_blocklist
#           subscribe['from'] = xmppbl.org
#           subscribe['pubsub']['subscription']['node'] = 'muc_bans_sha256'
            subscriptions = await XmppPubsub.get_node_subscriptions(
                self, jabber_id, node_id)
        await self['xep_0115'].update_caps()
        rooms = await XmppGroupchat.autojoin_to_groupchat(self)
        # See also get_joined_rooms of slixmpp.plugins.xep_0045
        for room in rooms:
            XmppStatus.send_status_message(self, room)
            self.add_event_handler(f'muc::{room}::got_online',
                partial(XmppEvents.on_muc_got_online, self))
            self.add_event_handler(f'muc::{room}::presence',
                partial(XmppEvents.on_muc_presence, self))
            self.add_event_handler(f'muc::{room}::self-presence',
                partial(XmppEvents.on_muc_self_presence, self))
        await asyncio.sleep(5)
        self.send_presence(
            #pshow='available',
            pstatus='🛡 KaikOut Moderation Bot')
        logger.debug(f'{function_name},,Finish')
