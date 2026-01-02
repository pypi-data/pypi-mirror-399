"""
Integration tests for MoodleGroups module.

These tests require a real Moodle instance and valid credentials.
Configure your environment by creating a .env file in the tests directory.
See .env.example for the required variables.

Run tests with: pytest tests/test_groups.py -v
Run specific test: pytest tests/test_groups.py::TestMoodleGroups::test_get_course_groups -v
"""

import pytest
import os
from dotenv import load_dotenv
from edutools_moodle import MoodleAPI
from edutools_moodle.base import MoodleAPIError


# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


@pytest.fixture(scope="module")
def moodle():
    """
    Create a MoodleAPI instance for testing.
    Requires MOODLE_URL and MOODLE_TOKEN environment variables.
    """
    url = os.getenv('MOODLE_URL')
    token = os.getenv('MOODLE_TOKEN')
    
    if not url or not token:
        pytest.skip("MOODLE_URL and MOODLE_TOKEN must be set in .env file")
    
    return MoodleAPI(url, token)


@pytest.fixture(scope="module")
def test_data():
    """
    Load test data from environment variables.
    """
    return {
        'course_id': int(os.getenv('COURSE_ID', 123)),
        'group_id': int(os.getenv('GROUP_ID', 1811)),
        'user_id': int(os.getenv('USER_ID', 776)),
        'grouping_id': int(os.getenv('GROUPING_ID', 64))
    }


class TestMoodleGroupsBasic:
    """Test basic group operations that read data."""
    
    def test_get_course_groups(self, moodle, test_data):
        """
        Test: Get all groups in a course.
        
        This test retrieves all groups for the specified course.
        Expected: Returns a list of group dictionaries.
        """
        print(f"\n📋 Testing get_course_groups for course_id={test_data['course_id']}")
        
        groups = moodle.groups.get_course_groups(test_data['course_id'])
        
        assert isinstance(groups, list), "Should return a list"
        print(f"✅ Found {len(groups)} groups in the course")
        
        if groups:
            print(f"   First group: {groups[0].get('name')} (ID: {groups[0].get('id')})")
            for group in groups:
                assert 'id' in group, "Each group should have an ID"
                assert 'name' in group, "Each group should have a name"
    
    def test_get_group_members(self, moodle, test_data):
        """
        Test: Get all members of a specific group.
        
        This test retrieves member IDs for the specified group.
        Expected: Returns a list of user IDs.
        """
        print(f"\n👥 Testing get_group_members for group_id={test_data['group_id']}")
        
        members = moodle.groups.get_group_members(test_data['group_id'])
        
        assert isinstance(members, list), "Should return a list of user IDs"
        print(f"✅ Found {len(members)} members in the group")
        
        if members:
            print(f"   Member IDs: {members[:5]}{'...' if len(members) > 5 else ''}")
            for member_id in members:
                assert isinstance(member_id, int), "Each member ID should be an integer"
    
    def test_get_group_members_info(self, moodle, test_data):
        """
        Test: Get detailed information about group members.
        
        This test retrieves full user information for group members.
        Expected: Returns a list of user dictionaries with details.
        """
        print(f"\n📇 Testing get_group_members_info for group_id={test_data['group_id']}")
        
        members_info = moodle.groups.get_group_members_info(test_data['group_id'])
        
        assert isinstance(members_info, list), "Should return a list"
        print(f"✅ Found {len(members_info)} members with full info")
        
        if members_info:
            first_member = members_info[0]
            print(f"   First member: {first_member.get('fullname')} (ID: {first_member.get('id')})")
            print(f"   Email: {first_member.get('email', 'N/A')}")
            
            for member in members_info:
                assert 'id' in member, "Each member should have an ID"
                assert 'fullname' in member, "Each member should have a fullname"
    
    def test_is_user_in_group(self, moodle, test_data):
        """
        Test: Check if a user is a member of a specific group.
        
        This test checks if the specified user is in the specified group.
        Expected: Returns True or False.
        """
        print(f"\n🔍 Testing is_user_in_group for user_id={test_data['user_id']}, group_id={test_data['group_id']}")
        
        is_member = moodle.groups.is_user_in_group(
            test_data['group_id'],
            test_data['user_id']
        )
        
        assert isinstance(is_member, bool), "Should return a boolean"
        print(f"✅ User {test_data['user_id']} {'IS' if is_member else 'IS NOT'} in group {test_data['group_id']}")
    
    def test_get_user_groups(self, moodle, test_data):
        """
        Test: Get all groups that a user belongs to in a course.
        
        This test retrieves all groups where the specified user is a member.
        Expected: Returns a list of group dictionaries.
        """
        print(f"\n📚 Testing get_user_groups for user_id={test_data['user_id']}, course_id={test_data['course_id']}")
        
        user_groups = moodle.groups.get_user_groups(
            test_data['course_id'],
            test_data['user_id']
        )
        
        assert isinstance(user_groups, list), "Should return a list"
        print(f"✅ User {test_data['user_id']} is in {len(user_groups)} group(s)")
        
        if user_groups:
            for group in user_groups:
                print(f"   - {group.get('name')} (ID: {group.get('id')})")
    
    def test_get_user_groups_with_names(self, moodle, test_data):
        """
        Test: Get list of group names that a user belongs to.
        
        This test retrieves just the names of groups where the user is a member.
        Expected: Returns a list of group names (strings).
        """
        print(f"\n🏷️  Testing get_user_groups_with_names for user_id={test_data['user_id']}")
        
        group_names = moodle.groups.get_user_groups_with_names(
            test_data['course_id'],
            test_data['user_id']
        )
        
        assert isinstance(group_names, list), "Should return a list"
        print(f"✅ User is in groups: {group_names if group_names else '(none)'}")
        
        for name in group_names:
            assert isinstance(name, str), "Each group name should be a string"
    
    def test_get_all_course_groups_dict(self, moodle, test_data):
        """
        Test: Get all groups as a dictionary mapping names to IDs.
        
        This test retrieves groups in a convenient dictionary format.
        Expected: Returns a dict with group names as keys and IDs as values.
        """
        print(f"\n📖 Testing get_all_course_groups_dict for course_id={test_data['course_id']}")
        
        groups_dict = moodle.groups.get_all_course_groups_dict(test_data['course_id'])
        
        assert isinstance(groups_dict, dict), "Should return a dictionary"
        print(f"✅ Found {len(groups_dict)} groups as dict")
        
        if groups_dict:
            # Show first few groups
            items = list(groups_dict.items())[:3]
            for name, gid in items:
                print(f"   - '{name}': {gid}")
            
            for name, gid in groups_dict.items():
                assert isinstance(name, str), "Keys should be strings (group names)"
                assert isinstance(gid, int), "Values should be integers (group IDs)"
    
    def test_get_group_by_name(self, moodle, test_data):
        """
        Test: Find a group by name.
        
        First, we get a group name from the course, then search for it.
        Expected: Returns the group dictionary or None.
        """
        print(f"\n🔎 Testing get_group_by_name")
        
        # First, get a group name to search for
        groups = moodle.groups.get_course_groups(test_data['course_id'])
        
        if not groups:
            pytest.skip("No groups in course to test with")
        
        test_group_name = groups[0]['name']
        print(f"   Searching for group: '{test_group_name}'")
        
        found_group = moodle.groups.get_group_by_name(
            test_data['course_id'],
            test_group_name
        )
        
        assert found_group is not None, "Should find the group"
        assert found_group['name'] == test_group_name, "Should return correct group"
        print(f"✅ Found group: {found_group['name']} (ID: {found_group['id']})")
        
        # Test with non-existent group
        non_existent = moodle.groups.get_group_by_name(
            test_data['course_id'],
            "NonExistentGroup_xyz123"
        )
        assert non_existent is None, "Should return None for non-existent group"
        print(f"✅ Correctly returns None for non-existent group")
    
    def test_get_group_id_by_name(self, moodle, test_data):
        """
        Test: Get group ID by name.
        
        Similar to get_group_by_name but returns only the ID.
        Expected: Returns group ID or None.
        """
        print(f"\n🆔 Testing get_group_id_by_name")
        
        # Get a group name to search for
        groups = moodle.groups.get_course_groups(test_data['course_id'])
        
        if not groups:
            pytest.skip("No groups in course to test with")
        
        test_group_name = groups[0]['name']
        expected_id = groups[0]['id']
        print(f"   Searching for group: '{test_group_name}' (expected ID: {expected_id})")
        
        found_id = moodle.groups.get_group_id_by_name(
            test_data['course_id'],
            test_group_name
        )
        
        assert found_id == expected_id, "Should return correct group ID"
        print(f"✅ Found group ID: {found_id}")
        
        # Test with non-existent group
        non_existent_id = moodle.groups.get_group_id_by_name(
            test_data['course_id'],
            "NonExistentGroup_xyz123"
        )
        assert non_existent_id is None, "Should return None for non-existent group"
        print(f"✅ Correctly returns None for non-existent group")


class TestMoodleGroupsWriteOperations:
    """
    Test group operations that modify data.
    
    WARNING: These tests will modify your Moodle instance!
    They create, modify, and delete groups. Use with caution.
    """
    
    @pytest.fixture(scope="class")
    def test_group_name(self):
        """Generate a unique test group name."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"TestGroup_{timestamp}"
    
    def test_create_group(self, moodle, test_data, test_group_name):
        """
        Test: Create a new group.
        
        This test creates a new group in the course.
        Expected: Returns group creation response with ID.
        """
        print(f"\n➕ Testing create_group: '{test_group_name}'")
        
        response = moodle.groups.create_group(
            test_data['course_id'],
            test_group_name,
            description="Test group created by automated test"
        )
        
        assert isinstance(response, list), "Should return a list"
        assert len(response) > 0, "Should have at least one item"
        assert 'id' in response[0], "Should contain group ID"
        
        group_id = response[0]['id']
        print(f"✅ Created group '{test_group_name}' with ID: {group_id}")
        
        # Store for cleanup
        test_data['created_group_id'] = group_id
    
    def test_create_or_get_group_existing(self, moodle, test_data, test_group_name):
        """
        Test: Create or get existing group.
        
        This test checks that create_or_get_group returns existing group ID.
        Expected: Returns the ID of the previously created group.
        """
        print(f"\n🔄 Testing create_or_get_group for existing group: '{test_group_name}'")
        
        group_id = moodle.groups.create_or_get_group(
            test_data['course_id'],
            test_group_name,
            description="This should not be created"
        )
        
        assert group_id == test_data['created_group_id'], "Should return existing group ID"
        print(f"✅ Correctly returned existing group ID: {group_id}")
    
    def test_create_or_get_group_new(self, moodle, test_data):
        """
        Test: Create or get new group.
        
        This test checks that create_or_get_group creates a new group.
        Expected: Creates and returns new group ID.
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_group_name = f"TestGroupNew_{timestamp}"
        
        print(f"\n➕ Testing create_or_get_group for new group: '{new_group_name}'")
        
        group_id = moodle.groups.create_or_get_group(
            test_data['course_id'],
            new_group_name,
            description="Test group for create_or_get"
        )
        
        assert isinstance(group_id, int), "Should return group ID"
        print(f"✅ Created new group with ID: {group_id}")
        
        # Store for cleanup
        test_data['created_group_id_2'] = group_id
    
    def test_add_user_to_group(self, moodle, test_data):
        """
        Test: Add a user to a group.
        
        This test adds the specified user to the test group.
        Expected: Successfully adds user to group.
        """
        if 'created_group_id' not in test_data:
            pytest.skip("Test group not created")
        
        print(f"\n👤 Testing add_user_to_group: user={test_data['user_id']}, group={test_data['created_group_id']}")
        
        response = moodle.groups.add_user_to_group(
            test_data['created_group_id'],
            test_data['user_id']
        )
        
        # Verify user was added
        is_member = moodle.groups.is_user_in_group(
            test_data['created_group_id'],
            test_data['user_id']
        )
        
        assert is_member, "User should be in the group after adding"
        print(f"✅ User {test_data['user_id']} successfully added to group {test_data['created_group_id']}")
    
    def test_remove_member_from_group(self, moodle, test_data):
        """
        Test: Remove a user from a group.
        
        This test removes the previously added user from the test group.
        Expected: Successfully removes user from group.
        """
        if 'created_group_id' not in test_data:
            pytest.skip("Test group not created")
        
        print(f"\n➖ Testing remove_member_from_group: user={test_data['user_id']}, group={test_data['created_group_id']}")
        
        # First ensure user is in the group
        moodle.groups.add_user_to_group(
            test_data['created_group_id'],
            test_data['user_id']
        )
        
        # Now remove
        response = moodle.groups.remove_member_from_group(
            test_data['created_group_id'],
            test_data['user_id']
        )
        
        # Verify user was removed
        is_member = moodle.groups.is_user_in_group(
            test_data['created_group_id'],
            test_data['user_id']
        )
        
        assert not is_member, "User should not be in the group after removal"
        print(f"✅ User {test_data['user_id']} successfully removed from group {test_data['created_group_id']}")
    
    def test_move_user_to_group(self, moodle, test_data):
        """
        Test: Move a user from one group to another.
        
        This test moves a user between two test groups.
        Expected: User is moved successfully.
        """
        if 'created_group_id' not in test_data or 'created_group_id_2' not in test_data:
            pytest.skip("Test groups not created")
        
        old_group = test_data['created_group_id']
        new_group = test_data['created_group_id_2']
        user_id = test_data['user_id']
        
        print(f"\n🔀 Testing move_user_to_group: user={user_id}, from={old_group} to={new_group}")
        
        # Add user to old group first
        moodle.groups.add_user_to_group(old_group, user_id)
        
        # Move user
        success = moodle.groups.move_user_to_group(
            test_data['course_id'],
            user_id,
            old_group,
            new_group
        )
        
        assert success, "Move operation should return True"
        
        # Verify user is not in old group
        in_old = moodle.groups.is_user_in_group(old_group, user_id)
        assert not in_old, "User should not be in old group"
        
        # Verify user is in new group
        in_new = moodle.groups.is_user_in_group(new_group, user_id)
        assert in_new, "User should be in new group"
        
        print(f"✅ User {user_id} successfully moved from group {old_group} to {new_group}")
        
        # Cleanup: remove from new group
        moodle.groups.remove_member_from_group(new_group, user_id)
    
    def test_batch_enroll_users_to_groups(self, moodle, test_data):
        """
        Test: Batch enroll multiple users to groups.
        
        This test enrolls users to groups in batch.
        Expected: Successfully enrolls users and reports results.
        """
        if 'created_group_id' not in test_data or 'created_group_id_2' not in test_data:
            pytest.skip("Test groups not created")
        
        print(f"\n📦 Testing batch_enroll_users_to_groups")
        
        # Get group names
        groups = moodle.groups.get_course_groups(test_data['course_id'])
        group_1_name = None
        group_2_name = None
        
        for group in groups:
            if group['id'] == test_data['created_group_id']:
                group_1_name = group['name']
            elif group['id'] == test_data['created_group_id_2']:
                group_2_name = group['name']
        
        if not group_1_name or not group_2_name:
            pytest.skip("Could not find test group names")
        
        enrollments = [
            {'user_id': test_data['user_id'], 'group_name': group_1_name},
        ]
        
        print(f"   Enrolling user {test_data['user_id']} to {group_1_name}")
        
        result = moodle.groups.batch_enroll_users_to_groups(
            test_data['course_id'],
            enrollments
        )
        
        assert 'success' in result, "Should have success count"
        assert 'errors' in result, "Should have errors list"
        assert result['success'] >= 1, "Should have at least 1 success"
        
        print(f"✅ Batch enrollment completed: {result['success']} success, {len(result['errors'])} errors")
        
        # Cleanup
        moodle.groups.remove_member_from_group(test_data['created_group_id'], test_data['user_id'])
    
    def test_delete_group(self, moodle, test_data):
        """
        Test: Delete a group.
        
        This test deletes the test groups created during tests.
        Expected: Successfully deletes groups.
        
        NOTE: This should run last to clean up test data.
        """
        print(f"\n🗑️  Testing delete_group")
        
        deleted_count = 0
        
        # Delete first test group
        if 'created_group_id' in test_data:
            print(f"   Deleting group ID: {test_data['created_group_id']}")
            response = moodle.groups.delete_group(test_data['created_group_id'])
            deleted_count += 1
            print(f"   ✅ Deleted group {test_data['created_group_id']}")
        
        # Delete second test group
        if 'created_group_id_2' in test_data:
            print(f"   Deleting group ID: {test_data['created_group_id_2']}")
            response = moodle.groups.delete_group(test_data['created_group_id_2'])
            deleted_count += 1
            print(f"   ✅ Deleted group {test_data['created_group_id_2']}")
        
        print(f"✅ Cleanup completed: deleted {deleted_count} test group(s)")


class TestMoodleGroupingsOperations:
    """Test grouping operations."""
    
    def test_create_or_get_grouping(self, moodle, test_data):
        """
        Test: Create or get a grouping.
        
        This test creates a new grouping or returns existing one.
        Expected: Returns grouping ID.
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        grouping_name = f"TestGrouping_{timestamp}"
        
        print(f"\n📁 Testing create_or_get_grouping: '{grouping_name}'")
        
        grouping_id = moodle.groups.create_or_get_grouping(
            test_data['course_id'],
            grouping_name,
            description="Test grouping created by automated test"
        )
        
        assert isinstance(grouping_id, int), "Should return grouping ID"
        print(f"✅ Created/got grouping '{grouping_name}' with ID: {grouping_id}")
        
        # Test getting existing grouping
        grouping_id_2 = moodle.groups.create_or_get_grouping(
            test_data['course_id'],
            grouping_name
        )
        
        assert grouping_id == grouping_id_2, "Should return same ID for existing grouping"
        print(f"✅ Correctly returned existing grouping ID: {grouping_id_2}")
        
        # Note: Groupings can't be easily deleted via API, so we leave it for manual cleanup


class TestMoodleCohortsOperations:
    """Test cohort operations."""
    
    def test_is_user_in_cohort_default(self, moodle, test_data):
        """
        Test: Check if user is in default cohort.
        
        This test checks cohort membership with default cohort name.
        Expected: Returns True or False.
        """
        print(f"\n🎓 Testing is_user_in_cohort for user_id={test_data['user_id']}")
        
        is_in_cohort = moodle.groups.is_user_in_cohort(test_data['user_id'])
        
        assert isinstance(is_in_cohort, bool), "Should return a boolean"
        print(f"✅ User {test_data['user_id']} {'IS' if is_in_cohort else 'IS NOT'} in default cohort")
    
    def test_is_user_in_cohort_custom(self, moodle, test_data):
        """
        Test: Check if user is in a custom cohort.
        
        This test checks cohort membership with a custom cohort name.
        Expected: Returns True or False (likely False for non-existent cohort).
        """
        cohort_name = "NonExistentCohort_xyz"
        print(f"\n🎓 Testing is_user_in_cohort with custom cohort: '{cohort_name}'")
        
        is_in_cohort = moodle.groups.is_user_in_cohort(
            test_data['user_id'],
            cohort_name
        )
        
        assert isinstance(is_in_cohort, bool), "Should return a boolean"
        print(f"✅ User {test_data['user_id']} {'IS' if is_in_cohort else 'IS NOT'} in cohort '{cohort_name}'")


# Test execution markers
# Mark tests that require write permissions
write_tests = pytest.mark.write
read_only_tests = pytest.mark.read_only

# Mark slow tests
slow_tests = pytest.mark.slow


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║          MoodleGroups Integration Test Suite                  ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Before running these tests:
    1. Create a .env file in the tests directory
    2. Add your Moodle credentials (see .env.example)
    3. Set COURSE_ID, GROUP_ID, USER_ID, and GROUPING_ID
    
    Run with:
        pytest tests/test_groups.py -v                    # All tests
        pytest tests/test_groups.py -v -k "Basic"        # Read-only tests
        pytest tests/test_groups.py -v -k "Write"        # Write tests
        pytest tests/test_groups.py::TestMoodleGroupsBasic::test_get_course_groups -v
    
    WARNING: Write tests will modify your Moodle instance!
    """)
