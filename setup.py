#!/usr/bin/env python
"""Install this package. Requires sdss3tools.

To use:
python setup.py install
"""
from ics_mhs_config import sdss3tools

sdss3tools.setup(
    description = "Common code base for PFS MHS actor system",
    name = "ics_mhs_config",
    debug=True,
)
