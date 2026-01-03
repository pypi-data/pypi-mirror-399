#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from slixmpp import JID
from kaikout.database import DatabaseToml
from kaikout.log import Logger
from kaikout.utilities import Documentation
from kaikout.xmpp.commands import XmppCommands
from kaikout.xmpp.message import XmppMessage
from kaikout.xmpp.muc import XmppMuc
from kaikout.xmpp.status import XmppStatus
from kaikout.xmpp.utilities import XmppUtilities
import sys
import time


logger = Logger(__name__)


    # for task in main_task:
    #     task.cancel()

    # Deprecated in favour of event "presence_available"
    # if not main_task:
    #     await select_file()


class XmppChat:


    async def process_message(self, message):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good practice to check the messages's type before
        processing or sending replies.

        Parameters
        ----------
        message : str
            The received message stanza. See the documentation
            for stanza objects and the Message stanza to see
            how it may be used.
        """

        # jid_bare = message['from'].bare
        # jid_full = str(message['from'])

        # Process commands.
        message_type = message['type']
        message_body = message['body']
        jid = message['from']
        jid_bare = jid.bare

        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},{jid_bare},Start')

        if (message.get_plugin('muc', check=True) and
            message_type in ('chat', 'groupchat', 'normal')):
            alias = message['muc']['nick']
            room = message['muc']['room']
            self_alias = XmppMuc.get_self_alias(self, jid_bare)
            
            if message_type == 'groupchat':
                if (alias == self.alias or
                    not XmppMuc.is_moderator(self, room, alias) or
                    (not message_body.startswith(self_alias + ' ') and
                     not message_body.startswith(self_alias + ',') and
                     not message_body.startswith(self_alias + '.') and
                     not message_body.startswith(self_alias + ':'))):
                    return
                else:
                    # Adding one to the length because of
                    # assumption that a comma or a dot is added
                    self_alias_length = len(self_alias) + 1
                    command = message_body[self_alias_length:].lstrip()
            elif message_type == 'chat':
                if (alias == self_alias or
                    not XmppMuc.is_moderator(self, jid_bare, alias)):
                    # TODO Count and alert of MUC-PM attempts
                    print(f'Occupant {alias} of group chat {jid_bare} is not approved.')
                    return
                else:
                    command = message_body

        # NOTE Remote session functionality be restored for operators.
        #elif message_type in ('chat', 'normal'):
            """
            command = message_body
            jid_full = jid.full
            room = self.sessions[jid_bare] if jid_bare in self.sessions else message_body
            status_mode = status_text = message_response = None
            # Start a configuration session

            if '@' in room:
                if room in XmppMuc.get_joined_rooms(self):
                    if XmppMuc.is_moderator(self, room, self.alias):
                        is_jid_of_moderators = await XmppUtilities.is_jid_of_moderators(
                            self, room, jid_full)
                        if jid_bare not in self.sessions:
                            if is_jid_of_moderators:
                            # alias = XmppMuc.get_alias(self, room, jid)
                            # if XmppMuc.is_moderator(self, room, alias):
                                room_owners = await XmppMuc.get_affiliation_list(
                                    self, room, 'owner')
                                if not room_owners:
                                    present_participants = XmppMuc.get_roster(
                                        self, room)
                                    present_owners_alias = []
                                    for participant in present_participants:
                                        affiliation = XmppMuc.get_affiliation(
                                            self, room, participant)
                                        if affiliation == 'owner':
                                            present_owners_alias.append(
                                                participant)
                                    present_owners = []
                                    for owner_alias in present_owners_alias:
                                        owner_jid_full = XmppMuc.get_full_jid(
                                            self, room, owner_alias)
                                        owner_jid_bare = owner_jid_full.split('/')[0]
                                        present_owners.append(owner_jid_bare)
                                    if not present_owners:
                                        # present_moderators = set(await XmppMuc.get_role_list(
                                        #     self, room, 'moderator'))
                                        room_admins = await XmppMuc.get_affiliation_list(
                                            self, room, 'admin')
                                # NOTE: Consideration, when there is no access
                                # to the list of owners from groupchat configuration
                                # then send a message to the groupchat - use alias
                                # instead of a Jabber ID.
                                jids_to_notify = room_owners or present_owners or room_admins
                                self.sessions[jid_bare] = room
                                message_response = (
                                    f'A session to configure group chat {room} '
                                    'has been established.')
                                status_mode = 'chat'
                                status_text = f'Session is opened: {room}'
                                for jid in jids_to_notify:
                                    message_notification = (
                                        f'A session for group chat {room} has '
                                        f'been activated by {jid_bare}')
                                    XmppMessage.send(
                                        self, jid, message_notification, 'chat')
                            else:
                                message_response = (
                                    'You do not appear to be a moderator of '
                                    f'group chat {room}')
                                status_mode = 'available'
                                status_text = (
                                    'Type the desired group chat - in which you '
                                    'are a moderator at - to configure')
                                moderators = set(await XmppMuc.get_role_list(
                                    self, room, 'moderator'))
                                message_notification = (
                                    'An unauthorized attempt to establish a '
                                    f'session for group chat {room} has been '
                                    f'made by {jid_bare}')
                                for moderator in moderators:
                                    jid_full = XmppMuc.get_full_jid(
                                        self, room, moderator)
                                    XmppMessage.send(self, jid_full,
                                        message_notification, 'chat')
                        elif is_jid_of_moderators:
                            room = self.sessions[jid_bare]
                        else:
                            del self.sessions[jid_bare]
                            message_response = (
                                'The session has been ended, because you are no '
                                f'longer a moderator at group chat {room}')
                            status_mode = 'away'
                            status_text = f'Session is closed: {room}'
                            moderators = set(await XmppMuc.get_role_list(
                                self, room, 'moderator'))
                            message_notification = (
                                f'The session for group chat {room} with former '
                                f'moderator {jid_bare} has been terminated.\n'
                                f'A termination message was sent to {jid_bare}')
                            for moderator in moderators:
                                jid_full = XmppMuc.get_full_jid(
                                    self, room, moderator)
                                XmppMessage.send(self, jid_full,
                                    message_notification, 'chat')
                    else:
                        message_response = (
                            f'KaikOut must be a moderator at group chat "{room}".')
                else:
                    message_response = (
                        f'KaikOut is not present in group chat {room}'
                        'A session will not begin if KaikOut is not present in '
                        'the desired group chat.\n'
                        f'Invite KaikOut to group chat {room}, and try again')
            else:
                message_response = (
                    f'The text "{room}" does not appear to be a valid '
                    'group chat Jabber ID.')
            if status_mode and status_text:
                XmppStatus.send_status_message(
                    self, jid_full, status_mode, status_text)
            if message_response:
                XmppMessage.send_reply(self, message, message_response)
                return
            """
        else:
            logger.error(
                f'{function_name},{jid_bare},Unknown message type {message_type} {str(message)}')
            return

        db_file = DatabaseToml.instantiate(self, room)

        # # Support private message via groupchat
        # # See https://codeberg.org/poezio/slixmpp/issues/3506
        # if message_type == 'chat' and message.get_plugin('muc', check=True):
        #     # jid_bare = message['from'].bare
        #     if (jid_bare == jid_full[:jid_full.index('/')]):
        #         # TODO Count and alert of MUC-PM attempts
        #         return

        command_time_start = time.time()

        command_lowercase = command.lower()

        # if not self.settings[room]['enabled']:
        #     if not command_lowercase.startswith('start'):
        #         return

        response = None
        if command_lowercase == 'terminate':
            del self.sessions[jid_bare]
            message_response = (
                f'The session for group chat {room} has been terminated.')
            XmppMessage.send_reply(self, message, message_response)
            status_mode = 'away'
            status_text = f'Session is closed: {room}'
            XmppStatus.send_status_message(
                self, jid_full, status_mode, status_text)
        elif command_lowercase.startswith('blacklist +'):
            value = command[11:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'jid_blacklist', True)
            else:
                response = 'No action has been taken.  Missing Jabber IDs.'
        elif command_lowercase.startswith('blacklist -'):
            value = command[11:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'jid_blacklist', False)
            else:
                response = 'No action has been taken.  Missing Jabber IDs.'
        elif command_lowercase == 'help':
            command_list = XmppCommands.print_help()
            response = ('Available command keys:\n'
                        f'```\n{command_list}\n```\n'
                        'Usage: `help <key>`')
        elif command_lowercase == 'help all':
            command_list = Documentation.manual(
                'commands.toml', section='all')
            response = f'Complete list of commands:\n```\n{command_list}\n```'
        elif command_lowercase.startswith('help'):
            command = command[5:].lower()
            command = command.split(' ')
            if len(command) == 2:
                command_root = command[0]
                command_name = command[1]
                command_list = Documentation.manual(
                    'commands.toml', section=command_root, command=command_name)
                if command_list:
                    command_list = ''.join(command_list)
                    response = (command_list)
                else:
                    response = f'KeyError for {command_root} {command_name}'
            elif len(command) == 1:
                command = command[0]
                command_list = Documentation.manual(
                    'commands.toml', command)
                if command_list:
                    command_list = ' '.join(command_list)
                    response = (f'Available command `{command}` keys:\n'
                                f'```\n{command_list}\n```\n'
                                f'Usage: `help {command} <command>`')
                else:
                    response = f'KeyError for {command}'
            else:
                response = ('Invalid. Enter command key '
                            'or command key & name')
        elif command_lowercase == 'info':
            entries = XmppCommands.print_info_list()
            response = ('Available command options:\n'
                        f'```\n{entries}\n```\n'
                        'Usage: `info <option>`')
        elif command_lowercase.startswith('info'):
            entry = command[5:].lower()
            response = XmppCommands.print_info_specific(entry)
        elif command_lowercase.startswith('action'):
            value = command[6:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'action', value)
                    atype = 'ban' if value else 'devoice'
                    response = f'Action has been set to {atype} ({value})'
                except:
                    response = 'Enter a numerical value.'
            else:
                response = str(self.settings[room]['action'])
        elif command_lowercase.startswith('allow +'):
            value = command[7:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'allow', True)
            else:
                response = 'No action has been taken.  Missing keywords.'
        elif command_lowercase.startswith('allow -'):
            value = command[7:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'allow', False)
            else:
                response = 'No action has been taken.  Missing keywords.'
        elif command_lowercase.startswith('ban'):
            if command[4:]:
                value = command[4:].split()
                alias = value[0]
                reason = ' '.join(value[1:]) if len(value) > 1 else None
                await XmppCommands.outcast(self, room, alias, reason)
        elif command_lowercase.startswith('bookmark +'):
            if XmppUtilities.is_operator(self, jid_bare):
                muc_jid = command[11:]
                response = await XmppCommands.bookmark_add(
                    self, muc_jid)
            else:
                response = 'This action is restricted.  Type: adding bookmarks.'
        elif command_lowercase.startswith('bookmark -'):
            if XmppUtilities.is_operator(self, jid_bare):
                muc_jid = command[11:]
                response = await XmppCommands.bookmark_del(
                    self, muc_jid)
            else:
                response = 'This action is restricted.  Type: removing bookmarks.'
        elif command_lowercase == 'bookmarks':
            if XmppUtilities.is_operator(self, jid_bare):
                response = await XmppCommands.print_bookmarks(self)
            else:
                response = 'This action is restricted.  Type: viewing bookmarks.'
        elif command_lowercase.startswith('clear'):
            key = command[6:]
            response = await XmppCommands.clear_filter(
                self, room, db_file, key)
        elif command_lowercase.startswith('count'):
            value = command[5:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'count', value)
                    response = f'Count has been set to {value}'
                except:
                    response = ('No action has been taken.  '
                                'Enter a numerical value.')
            else:
                response = str(self.settings[room]['count'])
        elif command_lowercase.startswith('default'):
            key = command[8:]
            if key:
                response = await XmppCommands.restore_default(
                    self, room, db_file, key)
            else:
                response = 'No action has been taken.  Missing key.'
        elif command_lowercase == 'defaults':
            response = await XmppCommands.restore_default(
                self, room, db_file)
        elif command_lowercase.startswith('deny +'):
            value = command[6:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'deny', True)
            else:
                response = 'No action has been taken.  Missing keywords.'
        elif command_lowercase.startswith('deny -'):
            value = command[6:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'deny', False)
            else:
                response = 'No action has been taken.  Missing keywords.'
        elif command_lowercase == 'finished off':
            XmppCommands.update_setting_value(
                self, room, db_file, 'finished', 0)
            response = 'Finished indicator has deactivated.'
        elif command_lowercase == 'finished on':
            XmppCommands.update_setting_value(
                self, room, db_file, 'finished', 1)
            response = 'Finished indicator has activated.'
        elif command_lowercase.startswith('frequency messages'):
            value = command[18:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'frequency_messages', value)
                    response = ('Minimum allowed frequency for messages '
                                f'has been set to {value}')
                except:
                    response = 'Enter a numerical value.'
            else:
                response = str(self.settings[room]['frequency_messages'])
        elif command_lowercase.startswith('frequency presence'):
            value = command[18:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'frequency_presence', value)
                    response = ('Minimum allowed frequency for presence '
                                f'has been set to {value}')
                except:
                    response = 'Enter a numerical value.'
            else:
                response = str(self.settings[room]['frequency_presence'])
        elif command_lowercase == 'exit':
            if message_type == 'groupchat':
                await XmppCommands.muc_leave(self, room)
            else:
                response = 'This command is valid in groupchat only.'
        elif command_lowercase.startswith('ignore +'):
            value = command[8:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'rtbl_ignore', True)
            else:
                response = 'No action has been taken.  Missing Jabber IDs.'
        elif command_lowercase.startswith('ignore -'):
            value = command[8:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'rtbl_ignore', False)
            else:
                response = 'No action has been taken.  Missing Jabber IDs.'
        elif command_lowercase == 'inactivity off':
            XmppCommands.update_setting_value(
                self, room, db_file, 'check_inactivity', 0)
            response = 'Inactivity check has been deactivated.'
        elif command_lowercase == 'inactivity on':
            XmppCommands.update_setting_value(
                self, room, db_file, 'check_inactivity', 1)
            response = 'Inactivity check has been activated.'
        elif command_lowercase.startswith('inactivity span'):
            value = command[15:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'inactivity_span', value)
                    response = ('The maximum allowed time of inactivity '
                                f'has been set to {value} days')
                except:
                    response = 'Enter a numerical value.'
            else:
                response = str(self.settings[room]['inactivity_span'])
        elif command_lowercase.startswith('inactivity warn'):
            value = command[15:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'inactivity_warn', value)
                    response = ('The time of inactivity to send a warning '
                                f'upon before action has been set to {value} '
                                'minutes')
                except:
                    response = 'Enter a numerical value.'
            else:
                response = str(self.settings[room]['inactivity_warn'])
        elif command_lowercase.startswith('join'):
            muc_jid = command[5:]
            response = await XmppCommands.muc_join(self, muc_jid)
        elif command_lowercase == 'options':
            response = 'Options:\n```'
            response += XmppCommands.print_options(self, room)
            response += '\n```'
        elif command_lowercase.startswith('kick'):
            if command[5:]:
                value = command[5:].split()
                alias = value[0]
                reason = ' '.join(value[1:]) if len(value) > 1 else None
                await XmppCommands.kick(self, room, alias, reason)
        elif command_lowercase == 'message off':
            XmppCommands.update_setting_value(
                self, room, db_file, 'check_message', 0)
            response = 'Message check has been deactivated.'
        elif command_lowercase == 'message on':
            XmppCommands.update_setting_value(
                self, room, db_file, 'check_message', 1)
            response = 'Message check has been activated.'
        elif command_lowercase.startswith('score messages'):
            value = command[14:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'score_messages', value)
                    response = f'Score for messages has been set to {value}'
                except:
                    response = 'Enter a numerical value.'
            else:
                response = str(self.settings[room]['score_messages'])
        elif command_lowercase.startswith('score presence'):
            value = command[14:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'score_presence', value)
                    response = f'Score for presence has been set to {value}'
                except:
                    response = 'Enter a numerical value.'
            else:
                response = str(self.settings[room]['score_presence'])
        elif command_lowercase.startswith('scores reset'):
            jid_bare = command[12:].strip()
            if jid_bare:
                if jid_bare in self.settings[room]['scores']:
                    del self.settings[room]['scores'][jid_bare]
                    value = self.settings[room]['scores']
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'scores', value)
                    response = f'Score for {jid_bare} has been reset'
                else:
                    response = f'Jabber ID {jid_bare} is not known.'
            else:
                XmppCommands.update_setting_value(
                    self, room, db_file, 'scores', {})
                response = 'All scores have been reset'
        elif command_lowercase.startswith('scores'):
            jid_bare = command[6:].strip()
            if jid_bare:
                if jid_bare in self.settings[room]['scores']:
                    response = str(self.settings[room]['scores'][jid_bare])
                else:
                    response = f'Jabber ID {jid_bare} is not known.'
            else:
                response = str(self.settings[room]['scores'])
        elif command_lowercase == 'start':
            XmppCommands.update_setting_value(
                self, room, db_file, 'enabled', 1)
            XmppStatus.send_status_message(self, room)
        elif command_lowercase == 'stats':
            response = XmppCommands.print_statistics(db_file)
        elif command_lowercase == 'status off':
            XmppCommands.update_setting_value(
                self, room, db_file, 'check_status', 0)
            response = 'Status message check has been deactivated'
        elif command_lowercase == 'status on':
            XmppCommands.update_setting_value(
                self, room, db_file, 'check_status', 1)
            response = 'Status message check has been activated'
        elif command_lowercase == 'stop':
            XmppCommands.update_setting_value(
                self, room, db_file, 'enabled', 0)
            XmppStatus.send_status_message(self, room)
        elif command_lowercase == 'support':
            response = XmppCommands.print_support_jid()
            await XmppCommands.invite_jid_to_muc(self, room)
        elif command_lowercase.startswith('timer'):
            value = command[5:].strip()
            if value:
                try:
                    value = int(value)
                    XmppCommands.update_setting_value(
                        self, room, db_file, 'timer', value)
                    response = (
                        'Timer value for countdown before committing an action '
                        f'has been set to {value} seconds')
                except:
                    response = 'Enter a numerical value.'
            else:
                response = str(self.settings[room]['timer'])
        elif command_lowercase == 'version':
            response = XmppCommands.print_version()
        elif command_lowercase.startswith('whitelist +'):
            value = command[11:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'jid_whitelist', True)
            else:
                response = 'No action has been taken.  Missing Jabber IDs.'
        elif command_lowercase.startswith('whitelist -'):
            value = command[11:].strip()
            if value:
                response = XmppCommands.set_filter(
                    self, room, db_file, value, 'jid_whitelist', False)
            else:
                response = 'No action has been taken.  Missing Jabber IDs.'
        elif command_lowercase.startswith('xmpp:'):
            response = await XmppCommands.muc_join(self, command)
        else:
            response = XmppCommands.print_unknown()

        command_time_finish = time.time()
        command_time_total = command_time_finish - command_time_start
        command_time_total = round(command_time_total, 3)

        if response: XmppMessage.send_reply(self, message, response)

        if room in self.settings and self.settings[room]['finished']:
            response_finished = f'Finished. Total time: {command_time_total}s'
            XmppMessage.send_reply(self, message, response_finished)
