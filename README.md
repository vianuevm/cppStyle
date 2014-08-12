==========================================================================================================================
183 Style 1.0 
==========================================================================================================================

1) Clone the git hub repository.

2) Download pip if you do not have it (tool to install python dependencies).

http://pip.readthedocs.org/en/latest/installing.html

3) You will also need to run the command in the root directory of your project:

pip install virtualenv

4) This created a virtual environment for you to use.  You will need to activate the virtual environment:

In Mac/Linux:
In the root directory type:

a) virtualenv ENV
b) cd source ENV/bin/activate

In Windows (in dos):
In the root directory

a) virtualenv ENV
b) cd ENV\Scripts
c) activate

4) Now you need to run the command: 

Windows:
    venv\Scripts\pip install -r requirements.txt

Mac/Linux
    venv\bin\pip install -r requirements.txt

5) in the root directory you will need to create/setup the database

a) ./db_create.py
b) ./db_upgrade.py

6) In the root directory run the application:

    ./run.py 

7) Go to http://127.0.0.1:5000 - You're up and running locally for development!


Open Source Used:
==========================================================================================================================
  - The Style Grader takes advantage of google's cpplint for helping to parse some of the code, as well as stripping the code of garbage/comments
  -  PyParsing is used in cases where RegEx is not powerful enough to capture complex grammar (function prototypes, headers)
  - This project used Miguel Grindberg's microblog open source project as a base point for the backend web service.  He has an awesome tutorial on Flask web development here: http://blog.miguelgrinberg.com/

