"""
Test: Extra

Version: 6.1.1
Date updated: 30/12/2025 (dd/mm/yyyy)
"""

# Library
# ---------------------------------------------------------------------------
import pytest

from absfuyu import extra as ext


def test_ext_load():
    assert ext.is_loaded() is True
