#!/usr/bin/python
from style_grader_functions import *

#TODO: Set up standard error to print properly
def main():
    student_file_names = get_arguments(sys.argv[1:])
    sys.stderr = codecs.StreamReaderWriter(sys.stderr,
                                         codecs.getreader('utf8'),
                                         codecs.getwriter('utf8'),
                                         'replace')
    
    rubric = StyleRubric()
    #rubric.reset_error_count() # Is this line necessary?
    operator_space_tracker = OperatorSpace()

    for filename in student_file_names:
        rubric.reset_for_new_file() # Fixes issue with multiple command-line arguments
        grade_student_file(filename, rubric, operator_space_tracker)

#For debugging purposes only
    print "Total Errors: " + str(rubric.total_errors)
    for x, y in rubric.error_types.items():
        print x, y

 #function called on each filename function(fileName, rubric)

#print / send results
if __name__ == '__main__':
    main()
