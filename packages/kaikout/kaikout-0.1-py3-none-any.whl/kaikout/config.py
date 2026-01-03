#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from kaikout.log import Logger
import os
import sys
try:
    import tomllib
except:
    import tomli as tomllib

logger = Logger(__name__)


class Config:


    def get_default_data_directory():
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
        Determine the directory path where configuration will be stored.
    
        * If $XDG_CONFIG_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.

        Returns
        -------
        str
            Path to configuration directory.
        """
        # directory_config_home = xdg.BaseDirectory.xdg_config_home
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


    def get_values(filename, key=None):
        config_dir = Config.get_default_config_directory()
        if not os.path.isdir(config_dir):
            config_dir = '/usr/share/kaikout/'
        if not os.path.isdir(config_dir):
            config_dir = os.path.dirname(__file__) + "/assets"
        config_file = os.path.join(config_dir, filename)
        with open(config_file, mode="rb") as defaults:
            result = tomllib.load(defaults)
        values = result[key] if key else result
        return values
