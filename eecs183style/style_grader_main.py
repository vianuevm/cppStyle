#!/usr/bin/python
from eecs183style.style_grader_functions import print_success
from eecs183style.StyleRubric import StyleRubric
import sys

def main():
    # If there are filenames passed on the command line, use those; otherwise,
    # let the config reader get the file names.
    if len(sys.argv) > 1:
        student_files= sys.argv[1:]
    else:
        student_files = None

    rubric = StyleRubric(student_files=student_files)

    for filename in rubric.student_files:
        rubric.grade_student_file(filename)

    rubric.adjust_errors()

    rubric.print_errors()

#For debugging purposes only
    print "Total Errors: " + str(rubric.total_errors)
    for x, y in rubric.error_types.items():
        print x, y

    if rubric.total_errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()
