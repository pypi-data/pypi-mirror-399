"""
Unit and integration tests for edutools-moodle v0.2.0

This test suite validates all modules:
- MoodleBase: Response validation and error handling
- MoodleUsers: User management (7 functions)
- MoodleGroups: Groups, cohorts, groupings (20 functions)
- MoodleAssignments: Assignments and submissions (4 functions)
- MoodleGrades: Grade management (6 functions)

Usage:
    pytest tests/ -v                    # Run all tests
    pytest tests/test_users.py -v      # Run specific module
    pytest tests/ -k "test_get_grades" # Run specific test
"""

import pytest
import os
from dotenv import load_dotenv
from edutools_moodle import MoodleAPI
from edutools_moodle.base import MoodleAPIError

# Load test environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


@pytest.fixture(scope="session")
def moodle():
    """Create MoodleAPI instance for all tests."""
    url = os.getenv('MOODLE_URL')
    token = os.getenv('MOODLE_TOKEN')
    
    if not url or not token:
        pytest.skip("MOODLE_URL and MOODLE_TOKEN must be set in tests/.env")
    
    return MoodleAPI(url, token)


@pytest.fixture(scope="session")
def test_config():
    """Load test configuration from environment."""
    return {
        'course_id': int(os.getenv('COURSE_ID', 34)),
        'group_id': int(os.getenv('GROUP_ID', 1811)),
        'user_id': int(os.getenv('USER_ID', 1037)),
        'grouping_id': int(os.getenv('GROUPING_ID', 64)),
        'assignment_cmid': int(os.getenv('ASSIGNMENT_CMID', 957))
    }
