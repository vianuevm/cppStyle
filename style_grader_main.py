#!/usr/bin/python
from eecs183style.style_grader_functions import print_success
from eecs183style.StyleRubric import StyleRubric
import sys

<<<<<<< HEAD:style_grader_main.py
def style_grader_driver(online_files):
    rubric = StyleRubric()
    show_errors = []
=======
def main():
    # If there are filenames passed on the command line, use those; otherwise,
    # let the config reader get the file names.
    if len(sys.argv) > 1:
        student_files= sys.argv[1:]
    else:
        student_files = None

    rubric = StyleRubric(student_files=student_files)
>>>>>>> stevemer/master:eecs183style/style_grader_main.py

    # if online_submit:
    for filename in online_files:
        rubric.grade_student_file(filename)
    # else:
    #     for filename in rubric.student_files:
    #         rubric.grade_student_file(filename)

    rubric.adjust_errors()
    show_errors = rubric.print_errors(show_errors)
#For debugging purposes only
    print "Total Errors: " + str(rubric.total_errors)
    for x, y in rubric.error_types.items():
        print x, y

<<<<<<< HEAD:style_grader_main.py

    return show_errors

# if __name__ == '__main__':
#     main()
=======
    if rubric.total_errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
>>>>>>> stevemer/master:eecs183style/style_grader_main.py
