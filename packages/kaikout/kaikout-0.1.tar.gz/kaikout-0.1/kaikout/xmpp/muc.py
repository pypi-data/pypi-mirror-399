#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

1) Send message to inviter that bot has joined to groupchat.

2) If groupchat requires captcha, send the consequent message.

3) If groupchat error is received, send that error message to inviter.

FIXME

1) Save name of groupchat instead of jid as name

"""
from asyncio import TimeoutError
from kaikout.log import Logger
from slixmpp.exceptions import IqError, IqTimeout, PresenceError
import sys

logger = Logger(__name__)


class XmppMuc:


    def get_affiliation(self, room, alias):
        """Get an affiliation of a specified alias"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        affiliation = self.plugin['xep_0045'].get_jid_property(
            room, alias, 'affiliation')
        logger.debug(f'{function_name},{room},Finish')
        return affiliation


    async def get_affiliation_list(self, room, affiliation):
        """Get an affiliation list from groupchat config"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{affiliation}')
        try:
            jids = await self.plugin['xep_0045'].get_affiliation_list(
                room, affiliation)
        except Exception as e:
            jids = None
            logger.error(f'{function_name},{room},KaikOut has failed to query '
                         f'the server for a list of Jabber IDs with the '
                         f'affiliation "{affiliation}" for groupchat {room}')
            logger.error(e)
        logger.debug(f'{function_name},{room},Finish')
        return jids


    def get_alias(self, room, jid):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{jid}')
        alias = self.plugin['xep_0045'].get_nick(room, jid)
        logger.debug(f'{function_name},{room},Finish')
        return alias


    def get_full_jid(self, room, alias):
        """
        Get full JId.
    
        Parameters
        ----------
        jid_full : str
            Full Jabber ID.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        jid_full = self.plugin['xep_0045'].get_jid_property(
            room, alias, 'jid')
        logger.debug(f'{function_name},{room},Finish')
        return jid_full


    def get_joined_rooms(self):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        rooms = self.plugin['xep_0045'].get_joined_rooms()
        logger.debug(f'{function_name},,Finish')
        return rooms
    
    
    def get_role(self, room, alias):
        """Get a role of a specified alias"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        role = self.plugin['xep_0045'].get_jid_property(
            room, alias, 'role')
        logger.debug(f'{function_name},{room},Finish')
        return role


    async def get_role_list(self, room, role):
        """Get a role list from groupchat config"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        try:
            jids = await self.plugin['xep_0045'].get_roles_list(
                room, role)
            return jids
        except Exception as e:
            logger.error(f'{function_name},{room},KaikOut has failed to query '
                         'the server for a list of Jabber IDs with the role '
                         f'"{role}" for groupchat {room}')
            logger.error(f'{function_name},{jid_bare},{str(e)}')
        logger.debug(f'{function_name},{room},Finish')


    def get_roster(self, room):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        roster = self.plugin['xep_0045'].get_roster(room)
        logger.debug(f'{function_name},{room},Finish')
        return roster


    def get_self_alias(self, room):
        """Get self alias of a given group chat"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        jid_full = self.plugin['xep_0045'].get_our_jid_in_room(room)
        alias = jid_full.split('/')[1]
        logger.debug(f'{function_name},{room},Finish')
        return alias


    def is_admin(self, room, alias):
        """Check if given JID is an administrator"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        affiliation = self.plugin['xep_0045'].get_jid_property(
            room, alias, 'affiliation')
        result = True if affiliation == 'admin' else False
        logger.debug(f'{function_name},{room},Finish')
        return result


    def is_moderator(self, room, alias):
        """Check if given JID is a moderator"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        role = self.plugin['xep_0045'].get_jid_property(
            room, alias, 'role')
        result = True if role == 'moderator' else False
        logger.debug(f'{function_name},{room},Finish')
        return result


    # NOTE Would this properly work when Alias and Local differ?
    def is_member(self, jid_bare, jid_full):
        """Check if given JID is a member"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        logger.debug(f'{function_name},{jid_bare},{jid_full}')
        alias = jid_full[jid_full.index('/')+1:]
        affiliation = self.plugin['xep_0045'].get_jid_property(jid_bare, alias, 'affiliation')
        result = True if affiliation == 'member' else False
        logger.debug(f'{function_name},{jid_bare},Finish')
        return result


    def is_owner(self, room, alias):
        """Check if given JID is an owner"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        affiliation = self.plugin['xep_0045'].get_jid_property(
            room, alias, 'affiliation')
        result = True if affiliation == 'owner' else False
        logger.debug(f'{function_name},{room},Finish')
        return result


    async def join_to_muc(self, jid_bare, alias=None, password=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        if not alias: alias = self.alias
        try:
            await self.plugin['xep_0045'].join_muc_wait(
                jid_bare, alias, password=password, maxchars=0,
                maxstanzas=0, seconds=0, since=0, timeout=30)
                #presence_options = {"pfrom" : jid_from},
            result = 'success'
        except IqError as e:
            logger.error(f'{function_name},{jid_bare},Error XmppIQ')
            logger.error(f'{function_name},{jid_bare},{str(e)}')
            result = 'error'
        except IqTimeout as e:
            logger.error(f'{function_name},{jid_bare},Timeout XmppIQ')
            logger.error(f'{function_name},{jid_bare},{str(e)}')
            result = 'timeout'
        except TimeoutError as e:
            logger.error(f'{function_name},{jid_bare},Timeout AsyncIO')
            logger.error(f'{function_name},{jid_bare},{str(e)}')
            result = 'timeout'
        except PresenceError as e:
            logger.error(f'{function_name},{jid_bare},Error Presence')
            logger.error(f'{function_name},{jid_bare},{str(e)}')
            if (e.condition == 'forbidden' and
                e.presence['error']['code'] == '403'):
                logger.warning(f'{self.alias} is banned from {jid_bare}')
                result = 'ban'
            elif e.condition == 'conflict':
                logger.warning(f'{function_name},{jid_bare},{e.presence["error"]["text"]}')
                result = 'conflict'
            else:
                result = 'error'
        except Exception as e:
            logger.error(f'{function_name},{jid_bare},Unknown error')
            logger.error(f'{function_name},{jid_bare},{str(e)}')
            result = 'unknown'
        logger.debug(f'{function_name},{jid_bare},Finish')
        return result


    def leave(self, jid_bare):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')
        jid_bare_self = self.boundjid.bare if self.is_component else None
        message = ('This news bot will now leave this groupchat.\n'
                   f'The JID of this news bot is xmpp:{jid_bare_self}?message')
        status_message = ('This bot has left the group. '
                         f'It can be reached directly via {jid_bare_self}')
        self.send_message(mto=jid_bare, mfrom=self.boundjid.full,
                          mbody=message, mtype='groupchat')
        self.plugin['xep_0045'].leave_muc(
            jid_bare, self.alias, status_message, jid_bare_self)
        logger.debug(f'{function_name},{jid_bare},Finish')


    async def set_affiliation(
        self, room, affiliation, jid=None, alias=None, reason=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        try:
            await self.plugin['xep_0045'].set_affiliation(
                room, affiliation, jid=jid, nick=alias,
                reason=reason, ifrom=self.boundjid.bare)
        except IqError as e:
            logger.error(f'{function_name},{room},Error XmppIQ')
            logger.error(f'{function_name},{room},Could not set affiliation at room: {room}')
            logger.error(f'{function_name},{room},{str(e)}')
        except Exception as e:
            logger.error(f'{function_name},{room},Unknown error')
            logger.error(f'{function_name},{room},Could not set affiliation at room: {room}')
            logger.error(f'{function_name},{room},{str(e)}')
        logger.debug(f'{function_name},{room},Finish')


    async def set_role(self, room, alias, role, reason=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        try:
            await self.plugin['xep_0045'].set_role(
                room, alias, role, reason=None, ifrom=self.boundjid.bare)
        except IqError as e:
            logger.error(f'{function_name},{room},Error XmppIQ')
            logger.error(f'{function_name},{room},Could not set role of alias: {alias}')
            logger.error(f'{function_name},{room},{str(e)}')
        except Exception as e:
            logger.error(f'{function_name},{room},Unknown error')
            logger.error(f'{function_name},{room},Could not set role of alias: {alias}')
            logger.error(f'{function_name},{room},{str(e)}')
        logger.debug(f'{function_name},{room},Finish')
