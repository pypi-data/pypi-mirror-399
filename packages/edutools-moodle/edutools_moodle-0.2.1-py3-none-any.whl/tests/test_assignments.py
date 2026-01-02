"""
Tests for MoodleAssignments module (v0.2.0)

Tests 4 validated functions:
- get_assignments (optimized: 11 fields)
- get_assignment_id_by_cmid
- get_user_submission (optimized: 8 fields)

Note: get_assignment_submissions removed in v0.2.0 (deprecated API)
"""

import pytest
from edutools_moodle.base import MoodleAPIError


class TestMoodleAssignments:
    """Test assignment management functions."""
    
    def test_get_assignments(self, moodle, test_config):
        """Test getting assignments for a course (optimized in v0.2.0)."""
        assignments = moodle.assignments.get_assignments(
            course_ids=[test_config['course_id']]
        )
        
        assert isinstance(assignments, list)
        
        if assignments:
            # Verify optimized response (11 essential fields)
            assignment = assignments[0]
            assert 'id' in assignment
            assert 'name' in assignment
            assert 'course' in assignment
            
            # Verify fields are limited (optimization)
            assert len(assignment.keys()) <= 15, "Should return ~11 fields (optimized)"
    
    def test_get_assignment_id_by_cmid(self, moodle, test_config):
        """Test getting assignment ID from course module ID."""
        assignment_id = moodle.assignments.get_assignment_id_by_cmid(
            cmid=test_config['assignment_cmid'],
            course_id=test_config['course_id']
        )
        
        assert isinstance(assignment_id, int)
        assert assignment_id > 0
    
    def test_get_user_submission(self, moodle, test_config):
        """Test getting user submission (optimized in v0.2.0)."""
        # First get assignment ID
        assignment_id = moodle.assignments.get_assignment_id_by_cmid(
            cmid=test_config['assignment_cmid'],
            course_id=test_config['course_id']
        )
        
        # Get submission
        submission = moodle.assignments.get_user_submission(
            assignment_id=assignment_id,
            user_id=test_config['user_id']
        )
        
        # May return None if no submission
        if submission:
            # Verify optimized response (8 essential fields)
            assert 'id' in submission
            assert 'userid' in submission
            assert 'status' in submission
            assert len(submission.keys()) <= 12, "Should return ~8 fields (optimized)"
    
    def test_get_assignment_submissions_removed(self, moodle):
        """Verify get_assignment_submissions was removed in v0.2.0."""
        assert not hasattr(moodle.assignments, 'get_assignment_submissions'), \
            "get_assignment_submissions should be removed in v0.2.0"
