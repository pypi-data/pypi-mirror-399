#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Functions get_directory() were taken from project jarun/buku.
By Arun Prakash Jana (jarun) and Dmitry Marakasov (AMDmi3).
"""

import os
import sys
try:
    import tomllib
except:
    import tomli as tomllib

class Settings:

    def get_directory():
        """
        Determine the directory path where setting files be stored.
    
        * If $XDG_CONFIG_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.
    
        Returns
        -------
        str
            Path to configuration directory.
        """
    #    config_home = xdg.BaseDirectory.xdg_config_home
        config_home = os.environ.get('XDG_CONFIG_HOME')
        if config_home is None:
            if os.environ.get('HOME') is None:
                if sys.platform == 'win32':
                    config_home = os.environ.get('APPDATA')
                    if config_home is None:
                        return os.path.abspath('.')
                else:
                    return os.path.abspath('.')
            else:
                config_home = os.path.join(
                    os.environ.get('HOME'), '.config'
                    )
        return os.path.join(config_home, 'rivista')

    def get_setting(filename, section):
        with open(filename, mode="rb") as settings:
            result = tomllib.load(settings)[section]
        return result


class Data:

    def get_directory():
        """
        Determine the directory path where data files be stored.
    
        * If $XDG_DATA_HOME is defined, use it;
        * else if $HOME exists, use it;
        * else if the platform is Windows, use %APPDATA%;
        * else use the current directory.
    
        Returns
        -------
        str
            Path to database file.
        """
    #    data_home = xdg.BaseDirectory.xdg_data_home
        data_home = os.environ.get('XDG_DATA_HOME')
        if data_home is None:
            if os.environ.get('HOME') is None:
                if sys.platform == 'win32':
                    data_home = os.environ.get('APPDATA')
                    if data_home is None:
                        return os.path.abspath('.rivista/data')
                else:
                    return os.path.abspath('.rivista/data')
            else:
                data_home = os.path.join(
                    os.environ.get('HOME'), '.local', 'share'
                    )
        return os.path.join(data_home, 'rivista')

class Cache:

    def get_directory():
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
        cache_home = os.environ.get('XDG_CACHE_HOME')
        if cache_home is None:
            if os.environ.get('HOME') is None:
                if sys.platform == 'win32':
                    cache_home = os.environ.get('APPDATA')
                    if cache_home is None:
                        return os.path.abspath('.rivista/cache')
                else:
                    return os.path.abspath('.rivista/cache')
            else:
                cache_home = os.path.join(
                    os.environ.get('HOME'), '.cache'
                    )
        return os.path.join(cache_home, 'rivista')
