[![Build Status](https://travis-ci.org/stevemer/183style.png?branch=master)](https://travis-ci.org/stevemer/183style)
[![Coverage Status](https://coveralls.io/repos/stevemer/183style/badge.png)](https://coveralls.io/r/stevemer/183style)
[![Stories in Ready](https://badge.waffle.io/stevemer/183style.png?label=ready&title=Issues Ready)](http://waffle.io/stevemer/183style)

183_style_grader
==========================================================================================================================
This is a guide for those hoping to contribute who may begin and think - that's a lot of files!  The project is broken down into three main categories (subject to change for a web app)
Overview
==========================================================================================================================


1) style_grader_main.py: The small file that drives it all.  This file, in a nutshell, opens up the list of all student files, and for each file, the grader puts it through the code parsing process.  

------------------------------------------------------
    for filename in rubric.student_files:
        rubric.grade_student_file(filename)
------------------------------------------------------

- NOTE: rubric.ini: This file is how you tell the program WHAT files to grade.  So if you're debugging, or switch to a new file to grade or whatever, you have to change the first line:

[FILES]
student_files=hello.cpp


2) style_grader_classes.py: This holds the smaller classes that do not need their own file.  In addition to these, StyleError.py and StyleRubric.py have separate folder, as their functions and data constitute a huge portion of the project.

- Note: A large portion of the software's functions exist in StyleRubric and StyleError.

3) style_grader_functions.py: These are functions in addition to the StyleRubric and StyleError functions that drive the program.


Additional Files:
- multi_line_checks: These are functions called by the style grader function.  It contains the functions that must parse several lines of a file before determining whether there is an error or not (ie indentation, braces consistency).
- single_line_checks: Same as multi_line_checks, but for one-liners.
- regresson_test: Regression tests for the program (look'em up :)



How Does the Software Work
==========================================================================================================================
Step 1) The software opens ALL student files. (style_grader_main.py)

Step 2) The software loops through all files, calling "grade_student_file" function on all files. (style_grader_main.py)

Step 3) Once you call grade_student_file, you enter the StyleRubric class's function and begin grading one file. (StyleRubric.py)

Step 4) The grade_student_file function has two main objective:
  - Clean up the file (remove comments) and make sure it's properly formatted
  - Read the file LINE by LINE, on EACH line it calls all the of the functions in single_line_checks, multi_line_checks


** Important side rant: This is probably the most important design decision made - the file is analyzed on a line by line bases, so only one line at a time is judged for style.  If a multi_line_check finds a function, class, struct etc. then it will perform a sweep of that entire code block for indentation and bracing checks.  But that decision is based entirely on the parsing and analysis of a single line at a time.  This paradigm is to be held in any further development. **

Step 5) As stated previously, we are now checking each line through all of the style checking functions in StyleRubric.py and single_line_check.py and multi_line_check.py python files.  This is the line doing that magic:

==========================================================================================================================
       for self.current_line_num, code in enumerate(clean_code):
            for function in self.single_line_checks: function(self, code)
            for function in self.multi_line_checks: function(self, clean_lines)
==========================================================================================================================

- Note: DataStructureTracker and SpacingTracker are classes that help track data so that we can determine if there is an error or not.  For instance, DataStructureTracker counts the number of braces seen so far to make sure there are matching braces etc.

Step 6) If/when an error is discovered, the StyleRubric class adds an instance of the StyleError class to its ever growing list of errors.  This list (consider it similar to a vector for those C++ peeps) is always growing and ever present.

Step 7) Notice that StyleError instances capture quite a bit of information, marvel at technology.

Step 8) Once you've graded one student file, check to see if there are more (continue the for loop in step 1).  If not, spit out all the errors in a pretty ugly format that I'll be fixing with a UI/UX update in the near future.


Open Source Used:
==========================================================================================================================
  - The Style Grader takes advantage of google's cpplint for helping to parse some of the code, as well as stripping the code of garbage/comments
  -  PyParsing is used in cases where RegEx is not powerful enough to capture complex grammar (function prototypes, headers)

