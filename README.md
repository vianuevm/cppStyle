<<<<<<< HEAD
![alt tag](https://raw.github.com/vianuevm/183_style_grader/master/app/static/img/388.jpg)

#183 Style 1.0 


1) Clone the git hub repository.

2) Download pip if you do not have it (tool to install python dependencies).

> http://pip.readthedocs.org/en/latest/installing.html

3) You will also need to run the command in the root directory of your project:

> pip install virtualenv

4) This created a virtual environment for you to use.  You will need to activate the virtual environment:

In Mac/Linux:
-  virtualenv ENV
-  cd source ENV/bin/activate

In Windows (in dos):
- virtualenv ENV
- cd ENV\Scripts
- activate

5) Now you need to run the command: 

Windows:

> venv\Scripts\pip install -r requirements.txt


Mac/Linux

> venv\bin\pip install -r requirements.txt


6) in the root directory you will need to create/setup the database

- ./db_create.py
- ./db_upgrade.py

7) In the root directory run the application:

>  ./run.py 

8) Go to http://127.0.0.1:5000 - You're up and running locally for development!


Open Source Used:
==========================================================================================================================
  - The Style Grader takes advantage of google's cpplint for helping to parse some of the code, as well as stripping the code of garbage/comments
  -  PyParsing is used in cases where RegEx is not powerful enough to capture complex grammar (function prototypes, headers)
  - This project used Miguel Grindberg's microblog open source project as a base point for the backend web service.  He has an awesome tutorial on Flask web development here: http://blog.miguelgrinberg.com/
=======
183style <img style="float: right" src="seal.png" />
==========================================================================================================================

[![Build Status](https://travis-ci.org/stevemer/183style.png?branch=master)](https://travis-ci.org/stevemer/183style)
[![Coverage Status](https://coveralls.io/repos/stevemer/183style/badge.png?branch=master)](https://coveralls.io/r/stevemer/183style?branch=master)
[![Open bugs](https://badge.waffle.io/stevemer/183style.png?label=bug&title=Open%20Bugs)](https://waffle.io/stevemer/183style)
[![Stories in Ready](https://badge.waffle.io/stevemer/183style.png?label=ready&title=Ready)](http://waffle.io/stevemer/183style)


183style is the automated C++ style grader written for and used by EECS 183 at the University of Michigan.

##Installing

For now, just ```git clone``` the repository - eventually this will be packaged and added to PyPI.

##Getting Started with 183style

We'll let you know as soon as we know!

##Release Notes

ReadTheDocs coming soon, once things actually work well enough to merit documentation.

##Development

183style is still in development, and contributions are welcome! Fork away and have at it. Here's how the package works at the moment:

1) style_grader_main.py (driver) creates a StyleRubric, which does the heavy lifting.

2) StyleRubric.load_functions pulls all enabled functionalities out of rubric.ini, looks them up in their respective files and plugs them in for grading.

3) The StyleRubric then calls "grade_student_file" function on all files:

       for self.current_line_num, code in enumerate(clean_code):
            for function in self.single_line_checks: function(self, code)
            for function in self.multi_line_checks: function(self, clean_lines)
            ...
            

4) If an error is discovered, the StyleRubric class adds an instance of the StyleError class to its ever growing list of errors.  This list is eventually returned as the final result.


>>>>>>> stevemer/master

