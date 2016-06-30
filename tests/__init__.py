"""
Tests for vcdb.
"""
# Copyright (C) 2016 Thomas Aglassinger.
# Distributed under the GNU Lesser General Public License v3 or later.
import logging
import os.path

log = logging.getLogger('vcdb.tests')
TEMP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'temp'))
os.makedirs(TEMP_FOLDER, exist_ok=True)
