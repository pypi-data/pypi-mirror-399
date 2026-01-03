#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email.utils import parseaddr
import hashlib
from kaikout.log import Logger
#import kaikout.sqlite as sqlite
import os
import sys
import tomli_w
from urllib.parse import urlsplit

try:
    import tomllib
except:
    import tomli as tomllib

logger = Logger(__name__)


class Config:


    def get_default_data_directory():
        """
        Determine the directory path where data files be stored.
    
        * If $XDG_DATA_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.

        Returns
        -------
        str
            Path to data directory.
        """
        directory_home = os.environ.get('HOME')
        if directory_home:
            data_home = os.path.join(directory_home, '.local', 'share')
            return os.path.join(data_home, 'kaikout')
        elif sys.platform == 'win32':
            data_home = os.environ.get('APPDATA')
            if data_home is None:
                return 'kaikout_data'
        else:
            return 'kaikout_data'


    def get_default_config_directory():
        """
        Determine the directory path where configuration files be stored.
    
        * If $XDG_CONFIG_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.

        Returns
        -------
        str
            Path to configuration directory.
        """
    #    directory_config_home = xdg.BaseDirectory.xdg_config_home
        directory_config_home = os.environ.get('XDG_CONFIG_HOME')
        if directory_config_home is None:
            directory_home = os.environ.get('HOME')
            if directory_home is None:
                if sys.platform == 'win32':
                    directory_config_home = os.environ.get('APPDATA')
                    if directory_config_home is None:
                        return 'kaikout_config'
                else:
                    return 'kaikout_config'
            else:
                directory_config_home = os.path.join(directory_home, '.config')
        return os.path.join(directory_config_home, 'kaikout')

    def get_default_cache_directory():
        """
        Determine the directory path where cache files be stored.
    
        * If $XDG_CACHE_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.
    
        Returns
        -------
        str
            Path to cache directory.
        """
    #    cache_home = xdg.BaseDirectory.xdg_cache_home
        directory_cache_home = os.environ.get('XDG_CACHE_HOME')
        if directory_cache_home is None:
            directory_home = os.environ.get('HOME')
            if directory_home is None:
                if sys.platform == 'win32':
                    directory_cache_home = os.environ.get('APPDATA')
                    if directory_cache_home is None:
                        return 'kaikout_cache'
                else:
                    return 'kaikout_cache'
            else:
                directory_cache_home = os.path.join(directory_home, '.cache')
        return os.path.join(directory_cache_home, 'kaikout')


class Documentation:


    def manual(filename, section=None, command=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug('{}: filename: {}'.format(function_name, filename))
        config_dir = Config.get_default_config_directory()
        config_file = config_dir + '/' + filename
        cmds = Toml.open_file(config_file)
        if section == 'all':
            cmd_list = ''
            for cmd in cmds:
                for i in cmds[cmd]:
                    cmd_list += cmds[cmd][i] + '\n'
        elif command and section:
            try:
                cmd_list = cmds[section][command]
            except KeyError as e:
                logger.error(e)
                cmd_list = None
        elif section:
            try:
                cmd_list = []
                for cmd in cmds[section]:
                    cmd_list.extend([cmd])
            except KeyError as e:
                logger.error('KeyError:' + str(e))
                cmd_list = None
        else:
            cmd_list = []
            for cmd in cmds:
                cmd_list.extend([cmd])
        return cmd_list


class BlockList:


    def get_filename():
        """
        Get pathname of filename.
        If filename does not exist, create it.

        Parameters
        ----------
        None.
    
        Returns
        -------
        filename : str
            Pathname.
        """
        data_dir = Config.get_default_data_directory()
        if not os.path.isdir(data_dir): os.mkdir(data_dir)
        filename = os.path.join(data_dir, r"blocklist.toml")
        if not os.path.exists(filename):
            data = {'entries' : {}}
            Toml.save_file(filename, data)
        return filename

class String:

    def md5_hash(url):
        """
        Hash URL string to MD5 checksum.

        Parameters
        ----------
        url : str
            URL.
    
        Returns
        -------
        url_digest : str
            Hashed URL as an MD5 checksum.
        """
        url_encoded = url.encode()
        url_hashed = hashlib.md5(url_encoded)
        url_digest = url_hashed.hexdigest()
        return url_digest

class Toml:

    def open_file(filename: str) -> dict:
        with open(filename, mode="rb") as fn:
            data = tomllib.load(fn)
            return data

    def save_file(filename: str, data: dict) -> None:
        with open(filename, 'w') as fn:
            data_as_string = tomli_w.dumps(data)
            fn.write(data_as_string)

class Url:

    def check_xmpp_uri(uri):
        """
        Check validity of XMPP URI.

        Parameters
        ----------
        uri : str
            URI.
    
        Returns
        -------
        jid : str
            JID or None.
        """
        jid = urlsplit(uri).path
        if parseaddr(jid)[1] != jid:
            jid = False
        return jid
