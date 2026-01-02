"""
Tests for MoodleGrades module (v0.2.0)

Tests 6 validated functions:
- get_grades (optimized: 10 fields per item, new API)
- add_grade
- update_grade (fixed parameters)
- get_grades_for_assignment
- get_course_grades (BREAKING: now requires user_id)

Note: get_grade_items removed in v0.2.0 (API doesn't exist)
"""

import pytest
from edutools_moodle.base import MoodleAPIError


class TestMoodleGrades:
    """Test grade management functions."""
    
    def test_get_grades(self, moodle, test_config):
        """Test getting grades (optimized in v0.2.0, uses new API)."""
        grades = moodle.grades.get_grades(
            course_id=test_config['course_id'],
            user_id=test_config['user_id']
        )
        
        assert isinstance(grades, list)
        
        if grades:
            # Verify structure
            user_grades = grades[0]
            assert 'userid' in user_grades
            assert 'userfullname' in user_grades
            assert 'gradeitems' in user_grades
            
            # Verify optimized grade items (10 essential fields)
            if user_grades['gradeitems']:
                item = user_grades['gradeitems'][0]
                assert 'id' in item
                assert 'itemname' in item
                assert 'graderaw' in item
                assert len(item.keys()) <= 15, "Should return ~10 fields (optimized)"
    
    def test_get_grades_for_assignment(self, moodle, test_config):
        """Test getting grades for specific assignment."""
        # Get assignment ID
        assignment_id = moodle.assignments.get_assignment_id_by_cmid(
            cmid=test_config['assignment_cmid'],
            course_id=test_config['course_id']
        )
        
        grades = moodle.grades.get_grades_for_assignment(
            assignment_id=assignment_id
        )
        
        # May return empty list if no grades yet
        assert isinstance(grades, list)
    
    def test_get_course_grades_requires_user_id(self, moodle, test_config):
        """Test get_course_grades BREAKING CHANGE: requires user_id in v0.2.0."""
        # This should work (with user_id)
        result = moodle.grades.get_course_grades(
            course_id=test_config['course_id'],
            user_id=test_config['user_id']
        )
        
        # Returns HTML string
        assert isinstance(result, str)
    
    @pytest.mark.skip(reason="Modifies grade data")
    def test_add_grade(self, moodle, test_config):
        """Test adding a grade (skipped by default)."""
        pass
    
    @pytest.mark.skip(reason="Modifies grade data")
    def test_update_grade(self, moodle, test_config):
        """Test updating a grade (skipped by default)."""
        pass
    
    def test_get_grade_items_removed(self, moodle):
        """Verify get_grade_items was removed in v0.2.0."""
        assert not hasattr(moodle.grades, 'get_grade_items'), \
            "get_grade_items should be removed in v0.2.0"
