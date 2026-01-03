#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

class UtilityDate:

    def now():
        now = datetime.datetime.now(datetime.UTC)
        formatted_date = now.strftime('%Y-%m-%dT%H:%M:%SZ')
        return formatted_date
