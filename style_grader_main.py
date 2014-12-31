#!/usr/bin/python
from style_grader_functions import print_success
from StyleRubric import StyleRubric

def style_grader_driver(online_files):
    rubric = StyleRubric()
    show_errors = []

    for filename in online_files:
        rubric.grade_student_file(filename)

    rubric.adjust_errors()
    show_errors = rubric.print_errors(show_errors)
#For debugging purposes only
    print "Total Errors: " + str(rubric.total_errors)
    for x, y in rubric.error_types.items():
        print x, y


    return show_errors

# if __name__ == '__main__':
#     main()