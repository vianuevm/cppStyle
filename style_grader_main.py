#!/usr/bin/python
from style_grader_functions import print_success
from StyleRubric import StyleRubric

def grader(online_files):
    rubric = StyleRubric()

    # if online_submit:
    for filename in online_files:
        rubric.grade_student_file(filename)
    # else:
    #     for filename in rubric.student_files:
    #         rubric.grade_student_file(filename)

    rubric.adjust_errors()
    rubric.print_errors()
#For debugging purposes only
    show_errors = ""
    print "Total Errors: " + str(rubric.total_errors)
    for x, y in rubric.error_types.items():
        print x, y
        show_errors += x
        show_errors += " "
        show_errors += str(y)
        show_errors += '\n'


    return show_errors
 
# if __name__ == '__main__':
#     main()
