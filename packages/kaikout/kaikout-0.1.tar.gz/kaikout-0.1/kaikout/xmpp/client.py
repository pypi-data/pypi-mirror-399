#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import partial
from kaikout.about import Documentation
from kaikout.database import DatabaseToml, Record
from kaikout.log import Logger
from kaikout.utilities import Config, BlockList, Toml
from kaikout.xmpp.events import XmppEvents
import os
import slixmpp
import sys
import time

# time_now = datetime.now()
# time_now = time_now.strftime("%H:%M:%S")

# def print_time():
#     # return datetime.now().strftime("%H:%M:%S")
#     now = datetime.now()
#     current_time = now.strftime("%H:%M:%S")
#     return current_time

logger = Logger(__name__)

class XmppClient(slixmpp.ClientXMPP):

    """
    KaikOut - A moderation bot for Jabber/XMPP.
    KaikOut is a chat control bot for XMPP groupchats.
    """

    def __init__(self, jid, password, hostname, port, alias):
        slixmpp.ClientXMPP.__init__(self, jid, password, hostname, port, alias)

        # Get directories
        self.directory_config = Config.get_default_config_directory()
        self.directory_shared = Config.get_default_data_directory()

        # A handler for accounts.
        filename_accounts = os.path.join(self.directory_config, 'accounts.toml')
        self.data_accounts = Toml.open_file(filename_accounts)
        self.data_accounts_xmpp = self.data_accounts['xmpp']

        # A handler for blocklist.
        self.filename_blocklist = os.path.join(self.directory_shared, 'blocklist.toml')
        self.blocklist = Toml.open_file(self.filename_blocklist)

        # A handler for blocklist.
        filename_rtbl = os.path.join(self.directory_config, 'rtbl.toml')
        self.data_rtbl = Toml.open_file(filename_rtbl)

        # A handler for settings.
        filename_settings = os.path.join(self.directory_config, 'settings.toml')
        self.data_settings = Toml.open_file(filename_settings)

        # Handlers for action messages.
        self.actions = {}
        self.action_count = 0

        # A handler for alias.
        self.alias = alias

        # A handler for bookmarks.
        self.filename_bookmarks = os.path.join(self.directory_config, 'bookmarks.toml')
        self.data_bookmarks = Toml.open_file(self.filename_bookmarks)
        self.bookmarks = self.data_bookmarks['bookmarks']

        # A handler for configuration.
        self.defaults = self.data_settings['defaults']

        # Handlers for connectivity.
        self.connection_attempts = 0
        self.max_connection_attempts = 10
        self.task_ping_instance = {}
        self.reconnect_timeout = self.data_accounts_xmpp['settings']['reconnect_timeout']

        # A handler for operators.
        self.operators = self.data_accounts_xmpp['operators']

        # A handler for sessions.
        self.sessions = {}

        # A handler for settings.
        self.settings = {}

        # A handler for tasks.
        self.tasks = {}

        # Register plugins.
        xeps = [
            'xep_0004', # Data Forms
            'xep_0030', # Service Discovery
            'xep_0045', # Multi-User Chat
            'xep_0048', # Bookmarks
            'xep_0050', # Ad-Hoc Commands
            'xep_0060', # Publish-Subscribe
            'xep_0084', # User Avatar
            'xep_0085', # Chat State Notifications
            'xep_0115', # Entity Capabilities
            'xep_0122', # Data Forms Validation
            'xep_0199', # XMPP Ping
            'xep_0249', # Direct MUC Invitations
            'xep_0369', # Mediated Information eXchange (MIX)
            'xep_0437', # Room Activity Indicators
            'xep_0444', # Message Reactions
        ]

        for xep in xeps: self.register_plugin(xep)

        # Register events.
        events = [
#           ['chatstate_composing',
#            XmppEvents.on_chatstate_composing],
#           ['connection_failed',
#            XmppEvents.on_connection_failed],
            ['disco_info',
             XmppEvents.on_disco_info],
            ['groupchat_direct_invite',
             XmppEvents.on_groupchat_direct_invite], # XEP_0249
            ['groupchat_invite',
             XmppEvents.on_groupchat_invite], # XEP_0045
            ['message',
             XmppEvents.on_message],
            ['reactions',
             XmppEvents.on_reactions],
#           ['room_activity',
#            XmppEvents.on_room_activity],
#           ['session_resumed',
#            XmppEvents.on_session_resumed],
            ['session_start',
             XmppEvents.on_session_start],
        ]

        for event, handler in events:
            self.add_event_handler(
                event,
                partial(handler, self))

        # Connect and process.
        self.connect()
        self.loop.run_forever()
