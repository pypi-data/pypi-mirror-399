from edutools_moodle.api import MoodleAPI
# Moodle API Configuration for Testing
MOODLE_URL='https://cours.itformation.com'
MOODLE_TOKEN='5e70ab62a290315e3b376338996ee026'

# Course Information
COURSE_ID=34

# Test Data
GROUP_ID=1811
USER_ID=1037
GROUPING_ID=64

# MoodleBase test

api=MoodleAPI(MOODLE_URL, MOODLE_TOKEN)


#rs=api.users.create_user("najasoft2@gmail.com",'Aaaa@1111',"nnnnnn",'last name','najasoft2@gmail.com',)
#print(rs)
user_id=1361
# check_username_exists(username)
#exists=api.users.check_username_exists("najaaaasoft2@gmail.com")
#print("L'utilisateur existe",exists)
# send_notification
#sent=api.users.send_notification(user_id,"Test notification, Ceci est un message de test.")
#print("Notification envoyée:",sent)
#enroll_user_in_course
#rs=api.users.enroll_user_in_course(course_id=COURSE_ID,user_id=user_id)
#print("User enrolled in course:",rs)



#get_course_groups
#rs=api.groups.get_course_groups(course_id=COURSE_ID)
#for group in rs:
#  print(group)




group_id_test=2053





#add_user_to_group
#rs=api.groups.add_user_to_group(group_id=group_id_test,user_id=user_id)
#print("User added to group:",rs)

#remove_member_from_group
#rs=api.groups.remove_member_from_group(group_id=group_id_test,user_id=user_id)
#print("User removed from group:",rs)

#get_group_members
#rs=api.groups.get_group_members(group_id=GROUP_ID)
#for member in rs:
#    print(member)


group_id_test2=2054


grouping_id=68
cohort_name='Virt2526_1'
user_id_3=1259




cmid=957
mejbar_id=891
ass_id=api.assignments.get_assignment_id_by_cmid(cmid,COURSE_ID)

# Test add_grades (batch) - add grades for multiple students at once
grades_list = [
    {'userid': mejbar_id, 'grade': 1},
   
]

rs = api.grades.add_grades(assignment_id=ass_id, grades=grades_list)
print("Batch grades added:", rs)