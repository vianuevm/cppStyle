#!/usr/bin/python
from style_grader_functions import *
from StyleRubric import *

#TODO: Set up standard error to print properly
def main():
    
    sys.stderr = codecs.StreamReaderWriter(sys.stderr,
                                         codecs.getreader('utf8'),
                                         codecs.getwriter('utf8'),
                                         'replace')
    # Quick fix for now - ultimately this should be handled using argparse (TODO)
    if len(sys.argv) == 1:
        # No files were provided
        sys.stderr.write("Error: No files provided\n")
        # Should print usage info here, but argparse will autogen that - skipping this until that's decided
        sys.stderr.write("<Generic usage info>\n")
    
    args = get_arguments(sys.argv[1:])
    rubric = StyleRubric()

    if "student_files" in args.iterkeys():
        rubric.student_file_names = args["student_files"]
        rubric.student_file_names = rubric.clean_file(rubric.student_file_names)

    if "includes" in args.iterkeys():
        rubric.permitted_includes = args["includes"]
        rubric.permitted_includes = rubric.clean_file(rubric.permitted_includes)

    for filename in rubric.student_file_names:
        rubric.reset_for_new_file() # Fixes issue with multiple command-line arguments
        rubric.grade_student_file(filename)

    if not rubric.error_tracker:
        printSuccess()

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
