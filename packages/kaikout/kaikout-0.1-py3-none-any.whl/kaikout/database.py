#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from asyncio import Lock
import csv
from kaikout.log import Logger
from kaikout.utilities import Config, Toml
import os
import sys
import time

# from eliot import start_action, to_file
# # with start_action(action_type="list_feeds()", db=db_file):
# # with start_action(action_type="last_entries()", num=num):
# # with start_action(action_type="get_feeds()"):
# # with start_action(action_type="remove_entry()", source=source):
# # with start_action(action_type="search_entries()", query=query):
# # with start_action(action_type="check_entry()", link=link):

logger = Logger(__name__)


class DatabaseToml:


    def instantiate(self, room):
        """
        Callback function to instantiate action on database.

        Parameters
        ----------
        jid_file : str
            Filename.
        callback : ?
            Function name.
        message : str, optional
            Optional kwarg when a message is a part or
            required argument. The default is None.

        Returns
        -------
        object
            Coroutine object.
        """
        data_dir = DatabaseToml.get_default_data_directory()
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
        data_dir_toml = os.path.join(data_dir, 'toml')
        if not os.path.isdir(data_dir_toml):
            os.mkdir(data_dir_toml)
        filename = os.path.join(data_dir_toml, f'{room}.toml')
        if not os.path.exists(filename):
            DatabaseToml.create_settings_file(self, filename)
        DatabaseToml.load_jid_settings(self, room, filename)
        return filename


    def get_default_data_directory():
        if os.environ.get('HOME'):
            data_home = os.path.join(os.environ.get('HOME'), '.local', 'share')
            return os.path.join(data_home, 'kaikout')
        elif sys.platform == 'win32':
            data_home = os.environ.get('APPDATA')
            if data_home is None:
                return 'kaikout_data'
        else:
            return 'kaikout_data'


    def get_data_file(data_dir, room):
        toml_file = os.path.join(data_dir, 'toml', f'{room}.toml')
        return toml_file


    def create_settings_file(self, filename):
        Toml.save_file(filename, self.defaults)


    def load_jid_settings(self, room, filename):
        # data_dir = DatabaseToml.get_default_data_directory()
        # filename = DatabaseToml.get_data_file(data_dir, room)
        self.settings[room] = Toml.open_file(filename)


    def update_jid_settings(self, room, filename, key, value):
        data = Toml.open_file(filename)
        self.settings[room][key] = value
        Toml.save_file(filename, self.settings[room])


class Record:


    def jid_exist(filename, fields):
        """
        Confirm whether Alias and Jabber ID exist.

        Parameters
        ----------
        filename : str
            Filename.
        fields : list
            jid, alias, timestamp.
    
        Returns
        -------
        jid_exist: bool
            False or True.
        """
        jid_exist = False
        data_dir = Config.get_default_data_directory()
        data_dir_logs = os.path.join(data_dir, 'logs')
        csv_file = os.path.join(data_dir_logs, f'{filename}.csv')
        if (not os.path.isdir(data_dir) or
            not os.path.isdir(data_dir_logs) or
            not os.path.exists(csv_file)):
            jid_exist = False
        else:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                for line in reader:
                    if line[0] == fields[0]:
                        jid_exist = True
                        break
        return jid_exist


    def alias_jid_exist(filename, fields):
        """
        Confirm whether Alias and Jabber ID exist.

        Parameters
        ----------
        filename : str
            Filename.
        fields : list
            jid, alias, timestamp.
    
        Returns
        -------
        alias_jid_exist: bool
            False or True.
        """
        alias_jid_exist = False
        data_dir = Config.get_default_data_directory()
        data_dir_logs = os.path.join(data_dir, 'logs')
        csv_file = os.path.join(data_dir_logs, f'{filename}.csv')
        if (not os.path.isdir(data_dir) or
            not os.path.isdir(data_dir_logs) or
            not os.path.exists(csv_file)):
            alias_jid_exist = False
        else:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                for line in reader:
                    if line[0] == fields[0] and line[1] == fields[1]:
                        alias_jid_exist = True
                        break
        return alias_jid_exist


    def csv_jid(filename, fields):
        """
        Log Jabber ID to CSV file.

        Parameters
        ----------
        filename : str
            Filename.
        fields : list
            jid, alias, timestamp.
    
        Returns
        -------
        None.
        """
        data_dir = Config.get_default_data_directory()
        if not os.path.isdir(data_dir): os.mkdir(data_dir)
        data_dir_logs = os.path.join(data_dir, 'logs')
        if not os.path.isdir(data_dir_logs): os.mkdir(data_dir_logs)
        csv_file = os.path.join(data_dir_logs, f'{filename}.csv')
        if not os.path.exists(csv_file):
            columns = ['jid', 'alias', 'timestamp']
            with open(csv_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
        with open(csv_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)


    def csv(filename, fields):
        """
        Log message or presence to CSV file.

        Parameters
        ----------
        filename : str
            Filename.
        fields : list
            type, timestamp, alias, body, lang, and identifier.
    
        Returns
        -------
        None.
        """
        data_dir = Config.get_default_data_directory()
        if not os.path.isdir(data_dir): os.mkdir(data_dir)
        data_dir_logs = os.path.join(data_dir, 'logs')
        if not os.path.isdir(data_dir_logs): os.mkdir(data_dir_logs)
        csv_file = os.path.join(data_dir_logs, f'{filename}.csv')
        if not os.path.exists(csv_file):
            columns = ['type', 'timestamp', 'alias', 'body', 'lang', 'identifier']
            with open(csv_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
        with open(csv_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)


    def toml(self, room, fields, stanza_type):
        """
        Log message to TOML file.

        Parameters
        ----------
        room : str
            Group chat Jabber ID.
        fields : list
            alias, room, identifier, timestamp.
        stanza_type: str
            message or presence.
    
        Returns
        -------
        None.
        """
        alias, content, identifier, timestamp = fields
        data_dir = DatabaseToml.get_default_data_directory()
        filename = DatabaseToml.get_data_file(data_dir, room)
        # filename = room + '.toml'
        entry = {}
        entry['alias'] = alias
        entry['body'] = content
        entry['id'] = identifier
        entry['timestamp'] = timestamp
        activity_type = 'activity_' + stanza_type
        message_activity_list = self.settings[room][activity_type] if activity_type in self.settings[room] else []
        while len(message_activity_list) > 20: message_activity_list.pop(0)
        message_activity_list.append(entry)
        self.settings[room][activity_type] = message_activity_list # NOTE This directive might not be needed
        Toml.save_file(filename, self.settings[room])


