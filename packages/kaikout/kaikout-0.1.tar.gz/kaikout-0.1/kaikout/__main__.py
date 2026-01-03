#!/usr/bin/env python3

# Kaikout: Kaiko Out anti-spam bot for XMPP
# Copyright (C) 2024 Schimon Zackary
# This file is part of Kaikout.
# See the file LICENSE for copying permission.

# from kaikout.about import Documentation
from kaikout.log import Logger
from kaikout.utilities import Config, Toml
# from kaikout.xmpp.chat import XmppChat
from kaikout.xmpp.client import XmppClient
from kaikout.version import __version__
from getpass import getpass
from argparse import ArgumentParser
import os
import shutil
# import slixmpp
# import sys

def main():

    directory = os.path.dirname(__file__)

    # Copy data files
    directory_data = Config.get_default_config_directory()
    # TODO Utilize the actual data directory
    #directory_data = Config.get_default_data_directory()
    if not os.path.exists(directory_data):
        directory_assets = os.path.join(directory, 'assets')
        directory_assets_new = shutil.copytree(directory_assets, directory_data)
        print(f'Data directory {directory_assets_new} has been created and populated.')

    # Copy settings files
    directory_settings = Config.get_default_config_directory()
    if not os.path.exists(directory_settings):
        directory_configs = os.path.join(directory, 'configs')
        directory_settings_new = shutil.copytree(directory_configs, directory_settings)
        print(f'Configuration directory {directory_settings_new} has been created and populated.')

    # Setup the command line arguments.
    parser = ArgumentParser(description=XmppClient.__doc__)

    # Setup the command line arguments.
    parser.add_argument('-v', '--version', help='Print version',
                        action='version', version=__version__)
    parser.add_argument('--no-log', '--nolog', help='Do not create a log file',
                        action='store_const', dest='nolog',
                        const=True, default=False)

    # Output verbosity options.
    parser.add_argument('-d', '--debug', help='set logging to DEBUG',
                        action='store_const', dest='loglevel',
                        const='debug', default='info')
    parser.add_argument('-q', '--quiet', help='set logging to ERROR',
                        action='store_const', dest='loglevel',
                        const='error', default='info')
    parser.add_argument('-w', '--warning', help='set logging to WARNING',
                        action='store_const', dest='loglevel',
                        const='warn', default='info')

    args = parser.parse_args()

    # Create cache directories
    directory_cache = Config.get_default_cache_directory()
    if not os.path.exists(directory_cache):
        print(f'Creating a cache directory at {directory_cache}.')
        os.mkdir(directory_cache)

    # Setup logging.
    #logging.basicConfig(level=args.loglevel,
    #                    format='%(levelname)-8s %(message)s')

    filename_log = os.path.join(directory_cache, 'kaikout_log.csv')
    filename_log_old = os.path.join(directory_cache, 'kaikout_log.csv.old')
    if os.path.exists(filename_log): os.rename(filename_log, filename_log_old)
    loglevel = args.loglevel
    logger = Logger('kaikout')
    if not args.nolog:
        logger.set_filename(filename_log)
        with open(filename_log, 'a') as file:
            file.write('Time,,Level,Module,Function,JID/DB,Message\n')
    logger.set_level(loglevel)

    # Configure settings file
    file_settings = os.path.join(directory_settings, 'accounts.toml')
    if not os.path.exists(file_settings):
        directory_configs = os.path.join(directory, 'configs')
        file_settings_empty = os.path.join(directory_configs, 'accounts.toml')
        shutil.copyfile(file_settings_empty, file_settings)

    data_settings = Toml.open_file(file_settings)

    # Configure account
    data_settings_account = data_settings['xmpp']['client']

    settings_account = {
        'alias': 'Set an Alias',
        'jid': 'Set a Jabber ID',
        'password': 'Input Password'
    }

    for key in settings_account:
        data_settings_account_value = data_settings_account[key]
        if not data_settings_account_value:
            settings_account_message = settings_account[key]
            while not data_settings_account_value:
                if key == 'password':
                    data_settings_account_value = getpass(f'{settings_account_message}: ')
                else:
                    data_settings_account_value = input(f'{settings_account_message}: ')
            data_settings_account[key] = data_settings_account_value

    Toml.save_file(file_settings, data_settings)

    # Try configuration file
    jid = data_settings_account['jid']
    password = data_settings_account['password']
    alias = data_settings_account['alias']
    # TODO
    #hostname = account_xmpp_client['hostname'] if 'hostname' in account_xmpp_client else None
    #port = account_xmpp_client['port'] if 'port' in account_xmpp_client else None
    hostname = port = None
    XmppClient(jid, password, hostname, port, alias)

if __name__ == '__main__':
    main()
