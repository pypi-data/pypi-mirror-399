#!/usr/bin/python
# -*- coding: utf-8 -*-

# NOTE
# Consider to segregate this module into two parts;
# One for building, and one for server;
# In order to save memory.

import os
from rivista.parser.toml import ParserToml
from rivista.utility.config import Cache, Data, Settings

class PropertyPublish:

    directory_data = Data.get_directory()
    directory_output = os.path.join(directory_data, "output")
    directory_xmpp = os.path.join(directory_data, "xmpp")
    directory_enclosures = os.path.join(directory_data, "enclosures")
    directory_files = os.path.join(directory_data, "files")
    directory_source = os.path.join(directory_data, "source")
    directory_themes = os.path.join(directory_data, "themes")

    filename_icon = os.path.join(directory_output, "logo.svg")
    filename_logo = os.path.join(directory_output, "logo.svg")
    filename_atom = os.path.join(directory_output, "index.atom")
    filename_atom_gmi = os.path.join(directory_output, "index.gmi")
    filename_atom_html = os.path.join(directory_output, "index.html")
    filename_opml = os.path.join(directory_output, "collection.opml")
    filename_opml_gmi = os.path.join(directory_output, "collection.gmi")
    filename_opml_html = os.path.join(directory_output, "collection.html")
    filename_sitemap = os.path.join(directory_output, "sitemap.xml")

    directory_config = Settings.get_directory()

    filename_settings_gemtext = os.path.join(directory_config, "gemtext.toml")
    settings_gemtext = ParserToml.open_file(filename_settings_gemtext)
    gemtext_top = settings_gemtext["content"]["top"]
    gemtext_bottom = settings_gemtext["content"]["bottom"]

    filename_activity = os.path.join(directory_config, "activity.toml")
    activity = ParserToml.open_file(filename_activity)

    filename_mood = os.path.join(directory_config, "mood.toml")
    mood = ParserToml.open_file(filename_mood)

    directory_cache = Cache.get_directory()
    #directory_cache_json = os.path.join(directory_cache, "json")

    filename_settings = os.path.join(directory_config, "settings.toml")
    settings = ParserToml.open_file(filename_settings)

    filename_settings_map = os.path.join(directory_config, "map.toml")
    settings_map = ParserToml.open_file(filename_settings_map)

    domain_name_gemini = settings["domain-name"]["gemini"]
    domain_name_http = settings["domain-name"]["http"]

    theme = settings["stylesheet"]["theme"]

    document = settings["document"]
    locale = document["locale"]
    rights = document["rights"]

    settings_xmpp = settings["xmpp"]
    address = settings_xmpp["address"]
    password = settings_xmpp["password"]
    pubsub = settings_xmpp["publish"]["pubsub"]
    node = settings_xmpp["publish"]["node"]
    comments = settings_xmpp["publish"]["comments"]

publish_properties = PropertyPublish()
