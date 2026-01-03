#!/usr/bin/python
# -*- coding: utf-8 -*-

class UtilityText:

    def is_included(keywords: list, string: str):
        for keyword in keywords:
            #if string.index(keyword):
            if keyword in string:
                return True
