#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import kaikout.config as config
from kaikout.config import Config
from kaikout.log import Logger
from kaikout.database import DatabaseToml
from kaikout.utilities import Documentation, Toml, Url
from kaikout.version import __version__
from kaikout.xmpp.muc import XmppMuc
from kaikout.xmpp.status import XmppStatus
from kaikout.xmpp.utilities import XmppUtilities
from slixmpp.exceptions import IqError, IqTimeout
import sys
import time

try:
    import tomllib
except:
    import tomli as tomllib

logger = Logger(__name__)


    # for task in main_task:
    #     task.cancel()

    # Deprecated in favour of event "presence_available"
    # if not main_task:
    #     await select_file()

class XmppCommands:


    async def clear_filter(self, room, db_file, key):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{key}')
        value = []
        self.settings[room][key] = value
        DatabaseToml.update_jid_settings(self, room, db_file, key, value)
        message = 'Filter {} has been purged.'.format(key)
        logger.debug(f'{function_name},{room},Finish')
        return message


    async def devoice(self, room, alias, reason):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        status_message = (
            f'🚫 Committing an action (devoice) against participant {alias}')
        self.action_count += 1
        task_number = self.action_count
        if room not in self.actions: self.actions[room] = {}
        self.actions[room][task_number] = status_message
        XmppStatus.send_status_message(self, room)
        jid_full = XmppMuc.get_full_jid(self, room, alias)
        if jid_full:
            jid_bare = jid_full.split('/')[0]
            await XmppMuc.set_role(self, room, alias, 'visitor', reason)
        await asyncio.sleep(5)
        del self.actions[room][task_number]
        XmppStatus.send_status_message(self, room)
        logger.debug(f'{function_name},{room},Finish')
        return jid_bare


    async def countdown(self, time, room, alias, reason):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        while time > 1:
            time -= 1
            print([time, room, alias], end='\r')
            await asyncio.sleep(1)
        await XmppCommands.devoice(self, room, alias, reason)
        logger.debug(f'{function_name},{room},Finish')


    def fetch_gemini():
        message = 'Gemini and Gopher are not supported yet.'
        return message


    def get_interval(self, jid_bare):
        result = Config.get_setting_value(
            self.settings, jid_bare, 'interval')
        message = str(result)
        return message


    async def bookmark_add(self, muc_jid):
        if muc_jid not in self.bookmarks: self.bookmarks.append(muc_jid)
        Toml.save_file(self.filename_bookmarks, self.data_bookmarks)
        return f'Groupchat {muc_jid} has been added to bookmarks.'


    async def bookmark_del(self, muc_jid):
        if muc_jid in self.bookmarks: self.bookmarks.remove(muc_jid)
        Toml.save_file(self.filename_bookmarks, self.data_bookmarks)
        return f'Groupchat {muc_jid} has been removed from bookmarks.'


    async def invite_jid_to_muc(self, jid_bare):
        muc_jid = 'slixfeed@chat.woodpeckersnest.space'
        if await XmppUtilities.get_chat_type(self, jid_bare) == 'chat':
            self.plugin['xep_0045'].invite(muc_jid, jid_bare)


    async def kick(self, room, alias, reason):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        status_message = (
            f'🚫 Committing an action (kick) against participant {alias}')
        self.action_count += 1
        task_number = self.action_count
        if room not in self.actions: self.actions[room] = {}
        self.actions[room][task_number] = status_message
        XmppStatus.send_status_message(self, room)
        jid_full = XmppMuc.get_full_jid(self, room, alias)
        if jid_full:
            jid_bare = jid_full.split('/')[0]
            await XmppMuc.set_affiliation(
                self, room, 'none', jid_bare, reason)
        await asyncio.sleep(5)
        del self.actions[room][task_number]
        XmppStatus.send_status_message(self, room)
        logger.debug(f'{function_name},{room},Finish')
        return jid_bare


    async def muc_join(self, command):
        if command:
            muc_jid = Url.check_xmpp_uri(command)
            if muc_jid:
                # TODO probe JID and confirm it's a group chat
                result = await XmppMuc.join(self, muc_jid)
                if result == 'ban':
                    message = f'{self.alias} is banned from {muc_jid}'
                    if room in self.bookmarks: self.bookmarks.remove(room)
                else:
                    if room not in self.bookmarks: self.bookmarks.append(room)
                    message = f'Joined group chat {muc_jid}'
                Toml.save_file(self.filename_bookmarks, self.data_bookmarks)
            else:
                message = '> {muc_jid}\nGroup chat JID appears to be invalid.'
        else:
            message = '> {}\nGroup chat JID is missing.'
        return message


    async def muc_leave(self, room):
        XmppMuc.leave(self, room)
        if room in self.bookmarks: self.bookmarks.remove(room)
        Toml.save_file(self.filename_bookmarks, self.data_bookmarks)


    async def outcast(self, room, alias, reason):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        status_message = (
            f'🚫 Committing an action (ban) against participant {alias}')
        self.action_count += 1
        task_number = self.action_count
        if room not in self.actions: self.actions[room] = {}
        self.actions[room][task_number] = status_message
        XmppStatus.send_status_message(self, room)
        jid_full = XmppMuc.get_full_jid(self, room, alias)
        if jid_full:
            jid_bare = jid_full.split('/')[0]
            await XmppMuc.set_affiliation(self, room, 'outcast', jid_bare, reason)
        # else:
        #     # Could "alias" ever be relevant?
        #     # Being a moderator is essential to be able to outcast.
        #     # JIDs are visible to moderators.
        #     await XmppMuc.set_affiliation(self, room, 'outcast', alias, reason)
        await asyncio.sleep(5)
        del self.actions[room][task_number]
        XmppStatus.send_status_message(self, room)
        logger.debug(f'{function_name},{room},Finish')
        return jid_bare


    async def print_bookmarks(self):
        conferences = self.bookmarks
        message = '\nList of groupchats:\n\n```\n'
        for conference in conferences:
            message += f'{conference}\n'
        message += (f'```\nTotal of {len(conferences)} groupchats.\n')
        return message


    def print_help():
        result = Documentation.manual('commands.toml')
        message = '\n'.join(result)
        return message


    def print_help_list():
        command_list = Documentation.manual('commands.toml', section='all')
        message = (
            f'Complete list of commands:\n```\n{command_list}\n```')
        return message


    def print_help_specific(command_root, command_name):
        command_list = Documentation.manual(
            'commands.toml', section=command_root, command=command_name)
        if command_list:
            command_list = ''.join(command_list)
            message = (command_list)
        else:
            message = f'KeyError for {command_root} {command_name}'
        return message


    def print_help_key(command):
        command_list = Documentation.manual('commands.toml', command)
        if command_list:
            command_list = ' '.join(command_list)
            message = (
                f'Available command `{command}` keys:\n```\n{command_list}\n```'
                f'\nUsage: `help {command} <command>`')
        else:
            message = f'KeyError for {command}'
        return message


    def print_info_list():
        config_dir = config.get_default_config_directory()
        with open(config_dir + '/' + 'information.toml', mode="rb") as information:
            result = tomllib.load(information)
        message = '\n'.join(result)
        return message


    def print_info_specific(entry):
        config_dir = config.get_default_config_directory()
        with open(config_dir + '/' + 'information.toml', mode="rb") as information:
            entries = tomllib.load(information)
        if entry in entries:
            # command_list = '\n'.join(command_list)
            message = (entries[entry]['info'])
        else:
            message = f'KeyError for {entry}'
        return message


    def print_options(self, room):
        message = ''
        for key in self.settings[room]:
            val = self.settings[room][key]
            steps = 18 - len(key)
            pulse = ''
            for step in range(steps):
                pulse += ' '
            message += '\n' + key + pulse + ' = ' + str(val)
        return message


    def print_support_jid():
        muc_jid = 'slixfeed@chat.woodpeckersnest.space'
        message = 'Join xmpp:{}?join'.format(muc_jid)
        return message


    def print_unknown():
        message = 'An unknown command.  Type "help" for a list of commands.'
        return message


    def print_version():
        message = __version__
        return message


    def raise_score(self, room, alias, db_file, reason):
        """
        Raise score by one.

        Parameters
        ----------
        room : str
            Jabber ID.
        alias : str
            Alias.
        db_file : str
            Database filename.
        reason : str
            Reason.

        Returns
        -------
        result.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        status_message = (
            f'✒️ Writing a score against {alias} for {reason}')
        self.action_count += 1
        task_number = self.action_count
        if room not in self.actions: self.actions[room] = {}
        self.actions[room][task_number] = status_message
        XmppStatus.send_status_message(self, room)
        scores = self.settings[room]['scores'] if 'scores' in self.settings[room] else {}
        jid_full = XmppMuc.get_full_jid(self, room, alias)
        if jid_full:
            jid_bare = jid_full.split('/')[0]
            scores[jid_bare] = scores[jid_bare] + 1 if jid_bare in scores else 1
            DatabaseToml.update_jid_settings(
                self, room, db_file, 'scores', scores)
        time.sleep(5)
        del self.actions[room][task_number]
        XmppStatus.send_status_message(self, room)
        result = scores[jid_bare] if jid_full and jid_bare else 0
        logger.debug(f'{function_name},{room},Finish')
        return result


    def update_score_ban(self, room, jid_bare, db_file):
        """
        Update ban score.

        Parameters
        ----------
        room : str
            Jabber ID.
        jid_bare : str
            Jabber ID.
        db_file : str
            Database filename.

        Returns
        -------
        result.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{jid_bare}')
        scores = self.settings[room]['score_ban'] if 'score_ban' in self.settings[room] else {}
        scores[jid_bare] = scores[jid_bare] + 1 if jid_bare in scores else 1
        DatabaseToml.update_jid_settings(self, room, db_file, 'score_ban', scores)
        logger.debug(f'{function_name},{room},Finish')
        # result = scores[jid_bare]
        # return result


    def update_score_kick(self, room, jid_bare, db_file):
        """
        Update kick score.

        Parameters
        ----------
        room : str
            Jabber ID.
        jid_bare : str
            Jabber ID.
        db_file : str
            Database filename.

        Returns
        -------
        result.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{jid_bare}')
        scores = self.settings[room]['score_kick'] if 'score_kick' in self.settings[room] else {}
        scores[jid_bare] = scores[jid_bare] + 1 if jid_bare in scores else 1
        DatabaseToml.update_jid_settings(self, room, db_file, 'score_kick', scores)
        logger.debug(f'{function_name},{room},Finish')
        # result = scores[jid_bare]
        # return result


    def update_last_alias(self, room, jid_bare, db_file, alias):
        """
        Update last associated alias.

        Parameters
        ----------
        room : str
            Jabber ID.
        db_file : str
            Database filename.
        jid_bare : str
            Jabber ID.
        alias : 
            Alias.

        Returns
        -------
        None.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},JID: {jid_bare}; Alias: {alias}')
        associated = self.settings[room]['last_alias'] if 'last_alias' in self.settings[room] else {}
        associated[jid_bare] = alias
        DatabaseToml.update_jid_settings(self, room, db_file, 'last_alias', associated)
        logger.debug(f'{function_name},{room},Finish')


    def update_last_activity(self, room, jid_bare, db_file, timestamp):
        """
        Update last message activity.

        Parameters
        ----------
        room : str
            Jabber ID.
        db_file : str
            Database filename.
        jid_bare : str
            Jabber ID.
        timestamp : 
            Time stamp.

        Returns
        -------
        None.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},JID: {jid_bare}; Time: {timestamp}')
        activity = self.settings[room]['last_activity'] if 'last_activity' in self.settings[room] else {}
        activity[jid_bare] = timestamp
        DatabaseToml.update_jid_settings(self, room, db_file, 'last_activity', activity)
        logger.debug(f'{function_name},{room},Finish')


    def remove_last_activity(self, room, jid_bare, db_file):
        """
        Remove last message activity.

        Parameters
        ----------
        room : str
            Jabber ID.
        db_file : str
            Database filename.
        jid_bare : str
            Jabber ID.

        Returns
        -------
        result.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{jid_bare}')
        activity = self.settings[room]['last_activity'] if 'last_activity' in self.settings[room] else {}
        del activity[jid_bare]
        DatabaseToml.update_jid_settings(self, room, db_file, 'last_activity', activity)
        logger.debug(f'{function_name},{room},Finish')


    def raise_score_inactivity(self, room, alias, db_file):
        """
        Raise score by one.

        Parameters
        ----------
        room : str
            Jabber ID.
        alias : str
            Alias.
        db_file : str
            Database filename.

        Returns
        -------
        result.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{alias}')
        status_message = (
            f'✒️ Writing a score against {alias} for inactivity')
        self.action_count += 1
        task_number = self.action_count
        if room not in self.actions: self.actions[room] = {}
        self.actions[room][task_number] = status_message
        XmppStatus.send_status_message(self, room)
        scores_inactivity = self.settings[room]['scores_inactivity'] if 'scores_inactivity' in self.settings[room] else {}
        jid_full = XmppMuc.get_full_jid(self, room, alias)
        if jid_full:
            jid_bare = jid_full.split('/')[0]
            scores_inactivity[jid_bare] = scores_inactivity[jid_bare] + 1 if jid_bare in scores_inactivity else 1
            DatabaseToml.update_jid_settings(self, room, db_file, 'scores_inactivity', scores_inactivity)
        time.sleep(5)
        del self.actions[room][task_number]
        XmppStatus.send_status_message(self, room)
        result = scores_inactivity[jid_bare] if jid_full and jid_bare else 0
        logger.debug(f'{function_name},{room},Finish')
        return result


    async def restore_default(self, room, db_file, key=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{key}')
        if key:
            value = self.defaults[key]
            self.settings[room][key] = value
            # data_dir = DatabaseToml.get_default_data_directory()
            # db_file = DatabaseToml.get_data_file(data_dir, jid_bare)
            DatabaseToml.update_jid_settings(self, room, db_file, key, value)
            message = ('Setting {} has been restored to default value.'
                        .format(key))
        else:
            self.settings = self.defaults
            data_dir = DatabaseToml.get_default_data_directory()
            db_file = DatabaseToml.get_data_file(data_dir, room)
            DatabaseToml.create_settings_file(self, db_file)
            message = 'Default settings have been restored.'
        logger.debug(f'{function_name},{room},Finish')
        return message


    def set_filter(self, room, db_file, strings, filter, axis):
        """

        Parameters
        ----------
        db_file : str
            Database filename.
        strings : str
            string (word or phrase).
        filter : str
            'allow' or 'deny'.
        axis : boolean
            True for + (plus) and False for - (minus).

        Returns
        -------
        None.

        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{room},Start')
        logger.debug(f'{function_name},{room},{strings}')
        string_list = self.settings[room][filter] if filter in self.settings[room] else []
        new_strings = strings.split(',')
        processed_strings = []
        if axis:
            action = 'added to'
            for string in new_strings:
                if string and string not in string_list:
                    string_trim = string.strip()
                    string_list.append(string_trim)
                    processed_strings.append(string_trim)
        else:
            action = 'removed from'
            for string in new_strings:
                if string and string in string_list:
                    string_trim = string.strip()
                    string_list.remove(string_trim)
                    processed_strings.append(string_trim)
        DatabaseToml.update_jid_settings(self, room, db_file, filter, string_list)
        processed_strings.sort()
        if processed_strings:
            message = 'Strings "{}" have been {} list "{}".'.format(
                ', '.join(processed_strings), action, filter)
        else:
            message = 'Strings "{}" were already {} list "{}".'.format(
                strings, action, filter)
        logger.debug(f'{function_name},{room},Finish')
        return message


    async def set_interval(self, db_file, jid_bare, val):
        try:
            val_new = int(val)
            val_old = Config.get_setting_value(
                self.settings, jid_bare, 'interval')
            await Config.set_setting_value(
                self.settings, jid_bare, db_file, 'interval', val_new)
            message = ('Updates will be sent every {} minutes '
                       '(was: {}).'.format(val_new, val_old))
        except Exception as e:
            logger.error(str(e))
            message = ('No action has been taken.  Enter a numeric value only.')
        return message


    def update_setting_value(self, room, db_file, key, value):
        DatabaseToml.update_jid_settings(self, room, db_file, key, value)
