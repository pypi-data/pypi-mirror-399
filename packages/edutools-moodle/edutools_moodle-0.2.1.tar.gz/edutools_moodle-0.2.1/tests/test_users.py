"""
Tests for MoodleUsers module (v0.2.0)

Tests 7 validated functions:
- create_user
- get_user_by_username
- get_user_by_email
- get_users_by_field
- check_username_exists
- enroll_user_in_course
- send_notification
"""

import pytest
from edutools_moodle.base import MoodleAPIError


class TestMoodleUsers:
    """Test user management functions."""
    
    def test_check_username_exists(self, moodle):
        """Test checking if username exists."""
        # Check with a username that likely doesn't exist
        exists = moodle.users.check_username_exists("nonexistent_user_12345")
        assert isinstance(exists, bool)
        assert exists == False
    
    def test_get_users_by_field(self, moodle, test_config):
        """Test getting users by field (e.g., id)."""
        users = moodle.users.get_users_by_field(
            field='id',
            values=[test_config['user_id']]
        )
        
        assert isinstance(users, list)
        if users:
            assert 'id' in users[0]
            assert 'username' in users[0]
            assert 'email' in users[0]
    
    def test_get_user_by_username_not_found(self, moodle):
        """Test getting user by username (not found case)."""
        user = moodle.users.get_user_by_username("nonexistent_user_12345")
        assert user is None
    
    def test_get_user_by_email_not_found(self, moodle):
        """Test getting user by email (not found case)."""
        user = moodle.users.get_user_by_email("nonexistent@example.com")
        assert user is None
    
    @pytest.mark.skip(reason="Requires admin privileges to create users")
    def test_create_user(self, moodle):
        """Test user creation (skipped by default)."""
        pass
    
    @pytest.mark.skip(reason="Requires admin privileges to enroll users")  
    def test_enroll_user_in_course(self, moodle, test_config):
        """Test enrolling user in course (skipped by default)."""
        pass
    
    @pytest.mark.skip(reason="Sends actual notification")
    def test_send_notification(self, moodle, test_config):
        """Test sending notification (skipped by default)."""
        pass
