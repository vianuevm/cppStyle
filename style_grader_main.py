#!/usr/bin/python
from StyleRubric import StyleRubric

def main():
    rubric = StyleRubric()

    for filename in rubric.student_files:
        rubric.grade_student_file(filename)

    if not rubric.error_tracker:
        print_success()

    # print all errors
    for error in rubric.error_tracker:
        print error

#For debugging purposes only
    print "Total Errors: " + str(rubric.total_errors)
    for x, y in rubric.error_types.items():
        print x, y
 
if __name__ == '__main__':
    main()
