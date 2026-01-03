#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib.parse import parse_qs
from urllib.parse import urlparse

class UtilityUri:

    def parameters(string: str) -> dict:
        """
        Extract query parameters.
        """
        return parse_qs(urlparse(string).query)
        #uri_parsed = urlparse(str)
        #parameters = parse_qs(url_parsed.query)
        #return parameters

    def has_scheme(string: str) -> bool:
        """
        Check whether a string has a scheme.
        This function is meant to check whether a string is of local or external path.
        """
        try:
            if urlparse(string).scheme: return True
        except ValueError as value_error:
            if (len(value_error.args) and
                value_error.args[0] == "Invalid IPv6 URL" and
                string.startswith("ed2k://")): return True
