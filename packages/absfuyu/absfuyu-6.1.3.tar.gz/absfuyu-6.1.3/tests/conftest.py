"""
Global fixture

Version: 6.1.2
Date updated: 30/12/2025 (dd/mm/yyyy)
"""

import pytest


@pytest.fixture(scope="session")
def test_fixture_session():
    """This cache the fixture for current test session"""
    return None
