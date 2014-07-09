#!/usr/bin/python
from style_grader_functions import *
from StyleRubric import *

#TODO: Set up standard error to print properly
def main():

    """
    Adding something so revert is happy
    """
    sys.stderr = codecs.StreamReaderWriter(sys.stderr,
                                         codecs.getreader('utf8'),
                                         codecs.getwriter('utf8'),
                                         'replace')
   
    #TODO: Should use argparse here 
    args = get_arguments(sys.argv[1:])
    rubric = StyleRubric()

    for filename in rubric.student_files:
        rubric.reset_for_new_file() # Fixes issue with multiple command-line arguments
        rubric.grade_student_file(filename)

    if not rubric.error_tracker:
        printSuccess()

    rubric.error_tracker.sort()

    # print all errors
    for error in rubric.error_tracker:
        print error


#For debugging purposes only
    print "Total Errors: " + str(rubric.total_errors)
    for x, y in rubric.error_types.items():
        print x, y

 #function called on each filename function(fileName, rubric)

#print / send results
if __name__ == '__main__':
    main()
