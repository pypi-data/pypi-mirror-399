#!/usr/bin/python
# -*- coding: utf-8 -*-

#import importlib.resources

import os
from rivista.parser.toml import ParserToml
from rivista.parser.xml import ParserXml
from rivista.utility.config import Cache, Data, Settings
from rivista.utility.document import UtilityDocument
from rivista.utility.logger import UtilityLogger
from rivista.utility.rst import UtilityRst
#from rivista.utility.vcard import UtilityVCard
import shutil
import sys
import time

def start():
#    try:

        print("\n"
              "Rivista: Adjusting CSS and XSLT stylesheets."
              "\n")

        # Create directories
        directory_cache = Cache.get_directory()
        directory_data = Data.get_directory()
        directory_settings = Settings.get_directory()
        for directory in (directory_data, directory_settings, directory_cache):
            if not os.path.exists(directory):
                os.mkdir(directory)
                print(f"Creating directory {directory}")

        # Create cache directories
        for directory in ("edit", "comments"):
            pathname = os.path.join(directory_cache, directory)
            if not os.path.exists(pathname):
                os.mkdir(pathname)
                print(f"Creating directory {pathname}")

        # Create data directories
        for directory in ("output", "sockets"):
            pathname = os.path.join(directory_data, directory)
            if not os.path.exists(pathname):
                os.mkdir(pathname)
                print(f"Creating directory {pathname}")

        directory_self = os.path.dirname(__file__)
        #directory_self_data = os.path.join(directory_self, "data")
        # Change location reference of directory.
        directory_self_data = directory_self.replace("script", "data")

        # Copy configuration files
        directory_self_data_config = os.path.join(directory_self_data, "configs")
        for filename in os.listdir(directory_self_data_config):
            filename_settings = os.path.join(directory_settings, filename)
            if (not os.path.exists(filename_settings) or
                not os.path.getsize(filename_settings)):
                filename_original = os.path.join(directory_self_data_config,
                                                 filename)
                shutil.copyfile(filename_original, filename_settings)
                print(f"Copying file {filename_settings}")

        # Example copying a single file.
        #filename_graphics = os.path.join(directory_settings, "image.svg")
        #if (not os.path.exists(filename_graphics) or
        #    not os.path.getsize(filename_graphics)):
        #    filename_original = os.path.join(directory_self_data, "graphics", "image.svg")
        #    shutil.copyfile(filename_original, filename_graphics)
        #    print(f"Copying file {filename_graphics}")

        # Copy source files
        for kind in ("source", "themes"):
            directory_data_kind_self = os.path.join(directory_self_data, kind)
            directory_data_kind = os.path.join(directory_data, kind)
            if not os.path.exists(directory_data_kind):
                directory_data_kind_new = shutil.copytree(
                    directory_data_kind_self, directory_data_kind)
                print(f"Creating and populating directory {directory_data_kind_new}")

        # Copy data files
        directory_data_data = os.path.join(directory_data, "data")
        if not os.path.exists(directory_data_data): os.mkdir(directory_data_data)
        for kind in ("graphics", "scripts"):
            directory_data_kind_self = os.path.join(directory_self_data, kind)
            directory_data_kind = os.path.join(directory_data_data, kind)
            if not os.path.exists(directory_data_kind):
                directory_data_kind_new = shutil.copytree(
                    directory_data_kind_self, directory_data_kind)
                print(f"Creating and populating directory {directory_data_kind_new}")
        # Copy theme configuration
        filename_settings = os.path.join(directory_settings, "settings.toml")
        settings = ParserToml.open_file(filename_settings)
        theme = settings["stylesheet"]["theme"]
        # Copy stylesheet map file
        filename_stylesheet_configuration_theme = os.path.join(
            directory_data, "themes", theme, "map.toml")
        filename_stylesheet_configuration = os.path.join(
            directory_settings, "map.toml")
        filename_stylesheet_configuration_new = shutil.copyfile(
            filename_stylesheet_configuration_theme,
            filename_stylesheet_configuration)
        message = f"Copying stylesheet map file {filename_stylesheet_configuration_new}"
        print("Done.")
#    except KeyboardInterrupt:
#        sys.exit(0)
