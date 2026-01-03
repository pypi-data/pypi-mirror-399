#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
from typing import List, Dict

csv.register_dialect(
    "rivista",
    quotechar = "\"",
    skipinitialspace = True,
    lineterminator = "\n",
    strict = True)

class UtilityCsv:

    def parse_csv_to_dict(csv_string: str) -> List[Dict[str, str]]:
        # Split the input string into lines.
        lines = csv_string.strip().split("\n")
        # Parse CSV data.
        reader = csv.DictReader(lines, dialect="rivista")
        # Populate the parsed data into a list of dictionaries.
        result = [row for row in reader]
        return result
