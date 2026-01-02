"""
Grades module for Moodle API.

Handles operations related to grades and grading.
"""

from .base import MoodleBase
from typing import List, Dict, Any, Optional


class MoodleGrades(MoodleBase):
    """
    Class for managing grades in Moodle.
    """

    def add_grade(
        self,
        assignment_id: int,
        user_id: int,
        grade: float,
        attempt_number: int = -1,
        add_attempt: int = 0,
        workflow_state: str = "released",
        feedback_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a grade for a student in an assignment.

        Args:
            assignment_id: ID of the assignment
            user_id: ID of the student
            grade: Grade to assign (must be a float)
            attempt_number: Attempt number (-1 for current attempt)
            add_attempt: Whether to create a new attempt (0 or 1)
            workflow_state: Workflow state (e.g., "released", "draft")
            feedback_comment: Optional feedback comment for the student

        Returns:
            API response dictionary

        Raises:
            ValueError: If grade is not a valid number
        """
        try:
            grade = float(grade)
        except ValueError:
            raise ValueError(f"The grade provided ({grade}) is not a valid number.")

        params = {
            'assignmentid': assignment_id,
            'applytoall': 1,
            'grades[0][userid]': user_id,
            'grades[0][grade]': grade,
            'grades[0][attemptnumber]': attempt_number,
            'grades[0][addattempt]': add_attempt,
            'grades[0][workflowstate]': workflow_state,
        }

        # Add feedback comment if provided
        if feedback_comment:
            params['grades[0][plugindata][assignfeedbackcomments_editor][text]'] = feedback_comment
            params['grades[0][plugindata][assignfeedbackcomments_editor][format]'] = 1  # HTML format

        return self.call_api('mod_assign_save_grades', params)

    def add_grades(
        self,
        assignment_id: int,
        grades: List[Dict[str, Any]],
        applytoall: int = 1,
        attemptnumber: int = -1,
        addattempt: int = 0,
        workflowstate: str = "released"
    ) -> Dict[str, Any]:
        """
        Add grades for multiple students in an assignment (batch operation).

        Args:
            assignment_id: ID of the assignment
            grades: List of dictionaries containing grade information
                   Example: [{'userid': 1, 'grade': 85.5}, {'userid': 2, 'grade': 90.0}]
            applytoall: Whether grades apply to all attempts (1 by default)
            attemptnumber: Attempt number to apply the grade to (-1 for current)
            addattempt: Whether to create a new attempt (0 by default)
            workflowstate: Workflow state of the grades (e.g., "released" or "draft")

        Returns:
            API response dictionary

        Raises:
            TypeError: If grades is not a list
            ValueError: If grade entries are invalid
        """
        if not isinstance(grades, list):
            raise TypeError(f"The 'grades' parameter must be a list, received: {type(grades)}")

        # Validate and convert each grade entry
        for index, grade_entry in enumerate(grades):
            if 'userid' not in grade_entry or 'grade' not in grade_entry:
                raise ValueError(f"Each element in 'grades' must contain 'userid' and 'grade': {grade_entry}")

            try:
                grades[index]['grade'] = float(grade_entry['grade'])
            except ValueError:
                raise ValueError(f"The grade provided ({grade_entry['grade']}) is not a valid number.")

        # Build parameters for API
        params = {
            'assignmentid': assignment_id,
            'applytoall': applytoall
        }

        for index, grade_entry in enumerate(grades):
            params[f'grades[{index}][userid]'] = grade_entry['userid']
            params[f'grades[{index}][grade]'] = grade_entry['grade']
            params[f'grades[{index}][attemptnumber]'] = attemptnumber
            params[f'grades[{index}][addattempt]'] = addattempt
            params[f'grades[{index}][workflowstate]'] = workflowstate

        return self.call_api('mod_assign_save_grades', params)

    def get_grades(
        self, 
        course_id: int, 
        group_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get grades for a course, optionally filtered by group or user.

        Args:
            course_id: ID of the course
            group_id: Optional group ID to get grades for all users in a group
            user_id: Optional user ID to get grades for a specific user

        Returns:
            List of user grade dictionaries with simplified essential fields
        """
        params = {'courseid': course_id}
        if group_id:
            params['groupid'] = group_id
        if user_id:
            params['userid'] = user_id

        response = self.call_api('gradereport_user_get_grade_items', params)
        
        if isinstance(response, dict) and 'usergrades' in response:
            usergrades = response['usergrades']
            
            # Return only essential fields
            simplified_grades = []
            for usergrade in usergrades:
                simplified_user = {
                    'userid': usergrade.get('userid'),
                    'userfullname': usergrade.get('userfullname'),
                    'gradeitems': []
                }
                
                for item in usergrade.get('gradeitems', []):
                    simplified_item = {
                        'id': item.get('id'),
                        'itemname': item.get('itemname'),
                        'itemtype': item.get('itemtype'),
                        'itemmodule': item.get('itemmodule'),
                        'cmid': item.get('cmid'),
                        'graderaw': item.get('graderaw'),
                        'gradeformatted': item.get('gradeformatted'),
                        'grademin': item.get('grademin'),
                        'grademax': item.get('grademax'),
                        'feedback': item.get('feedback', '')
                    }
                    simplified_user['gradeitems'].append(simplified_item)
                
                simplified_grades.append(simplified_user)
            
            return simplified_grades
        
        return []

    def update_grade(
        self,
        assignment_id: int,
        user_id: int,
        grade: float,
        attempt_number: int = -1,
        add_attempt: int = 0,
        workflow_state: str = "released",
        feedback: str = ""
    ) -> Dict[str, Any]:
        """
        Update a grade for a user's assignment submission.

        Args:
            assignment_id: ID of the assignment
            user_id: ID of the user
            grade: Grade value
            attempt_number: Attempt number (-1 for current attempt)
            add_attempt: Whether to create a new attempt (0 or 1)
            workflow_state: Workflow state (e.g., "released", "draft")
            feedback: Optional feedback text

        Returns:
            API response
        """
        params = {
            'assignmentid': assignment_id,
            'applytoall': 1,
            'grades[0][userid]': user_id,
            'grades[0][grade]': grade,
            'grades[0][attemptnumber]': attempt_number,
            'grades[0][addattempt]': add_attempt,
            'grades[0][workflowstate]': workflow_state,
            # Always include feedback structure to avoid NULL errors
            'grades[0][plugindata][assignfeedbackcomments_editor][text]': feedback,
            'grades[0][plugindata][assignfeedbackcomments_editor][format]': 1  # HTML format
        }

        return self.call_api('mod_assign_save_grades', params)

    def get_course_grades(self, course_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get grades table for a specific user in a course.

        Args:
            course_id: ID of the course
            user_id: ID of the user (required to avoid timeout on large courses)

        Returns:
            Dictionary with grade table information for the user
            
        Note:
            This API returns formatted grade table data. For raw grade data,
            use get_grades() instead which is more flexible and efficient.
        """
        params = {
            'courseid': course_id,
            'userid': user_id
        }
        return self.call_api('gradereport_user_get_grades_table', params)

    # get_grade_items removed - API not available or not needed

    def get_grades_for_assignment(
        self,
        assignment_id: int,
        user_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get grades for specific users in an assignment.

        Args:
            assignment_id: ID of the assignment
            user_ids: Optional list of user IDs to filter by

        Returns:
            List of grade dictionaries for the assignment
        """
        params = {'assignmentids[0]': assignment_id}
        
        if user_ids:
            for i, user_id in enumerate(user_ids):
                params[f'userids[{i}]'] = user_id
        
        response = self.call_api('mod_assign_get_grades', params)
        
        if isinstance(response, dict) and 'assignments' in response:
            assignments = response.get('assignments', [])
            if assignments:
                return assignments[0].get('grades', [])
        
        return []

