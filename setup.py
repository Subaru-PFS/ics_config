#!/usr/bin/env python3
"""Install this package. Requires sdss3tools.

To use:
python3 setup.py install
"""
import sdss3tools

sdss3tools.setup(
    description = "Common code base for PFS MHS actor system",
    name = "ics_config",
)
